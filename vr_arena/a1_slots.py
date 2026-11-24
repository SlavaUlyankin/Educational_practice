"""Алгоритм А1 — проверка доступности слота и создание брони."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from .models import (
    HORIZON_H, MAX_ALTERNATIVES, PREP_MIN, STEP_MIN,
    Booking, BookingEventType, BookingHistory, BookingStatus,
    EquipmentSet, EquipmentStatus, Reason, SlotCheckResult,
)


def append_booking_history(
    history: list[BookingHistory], booking_id: int,
    event_type: BookingEventType, changed_at: datetime,
    old_start_time: Optional[datetime], new_start_time: Optional[datetime],
    old_arena_id: Optional[int], new_arena_id: Optional[int],
    reason: Optional[str] = None,
) -> BookingHistory:
    """Добавляет запись аудита; саму бронь функция не изменяет."""
    entry = BookingHistory(
        max((item.history_id for item in history), default=0) + 1,
        booking_id, event_type, changed_at,
        old_start_time, new_start_time, old_arena_id, new_arena_id, reason,
    )
    history.append(entry)
    return entry


def record_booking_event(booking, history, event_type, changed_at,
                         old_start_time, new_start_time, old_arena_id,
                         new_arena_id, reason):
    """Сохраняет событие в брони и при наличии — в общем журнале."""
    target = booking.history if history is None else history
    next_id = max((item.history_id for item in booking.history + target), default=0) + 1
    entry = append_booking_history(target, booking.booking_id, event_type, changed_at,
                                   old_start_time, new_start_time, old_arena_id,
                                   new_arena_id, reason)
    entry.history_id = next_id
    if target is not booking.history:
        booking.history.append(entry)


def check_slot_availability(
    start: datetime, duration_min: int, players: int,
    game_min: int, game_max: int,
    bookings: list[Booking], kits: list[EquipmentSet],
    now: datetime, prep_min: int = PREP_MIN,
    exclude_id: Optional[int] = None, arena_id: int = 1,
) -> SlotCheckResult:
    """Проверяет [start; start + duration + prep) только внутри одной арены."""
    if duration_min <= 0 or players < 1 or prep_min < 0 or arena_id < 1:
        return SlotCheckResult(False, Reason.INVALID_INPUT)
    if players < game_min or players > game_max:
        return SlotCheckResult(False, Reason.PLAYERS_OUT_OF_RANGE)
    if start < now:
        return SlotCheckResult(False, Reason.IN_THE_PAST)
    usable = sum(
        kit.arena_id == arena_id and kit.status != EquipmentStatus.FAULTY
        for kit in kits
    )
    if usable < players:
        return SlotCheckResult(False, Reason.NOT_ENOUGH_KITS)
    new_end = start + timedelta(minutes=duration_min + prep_min)
    for b in bookings:
        if (b.arena_id != arena_id or b.status != BookingStatus.CONFIRMED
                or b.booking_id == exclude_id):
            continue
        b_end = b.start + timedelta(minutes=b.duration_min + prep_min)
        if start < b_end and b.start < new_end:
            return SlotCheckResult(False, Reason.CONFLICT, b.booking_id)
    return SlotCheckResult(True, Reason.OK)


def find_alternative_slots(
    start: datetime, duration_min: int, players: int,
    game_min: int, game_max: int,
    bookings: list[Booking], kits: list[EquipmentSet],
    now: datetime, prep_min: int = PREP_MIN,
    exclude_id: Optional[int] = None,
    step_min: int = STEP_MIN, horizon_h: int = HORIZON_H,
    max_results: int = MAX_ALTERNATIVES, arena_id: int = 1,
) -> list[datetime]:
    """Возвращает ближайшие свободные начала, не более max_results."""
    result: list[datetime] = []
    t = start + timedelta(minutes=step_min)
    limit = start + timedelta(hours=horizon_h)
    while t <= limit and len(result) < max_results:
        r = check_slot_availability(
            t, duration_min, players, game_min, game_max,
            bookings, kits, now, prep_min, exclude_id, arena_id,
        )
        if r.available:
            result.append(t)
        t += timedelta(minutes=step_min)
    return result


def create_booking(
    client_id: int, game_id: int, tariff_id: int,
    start: datetime, duration_min: int, players: int, prepaid_amount: float,
    game_min: int, game_max: int,
    bookings: list[Booking], kits: list[EquipmentSet],
    now: datetime, prep_min: int = PREP_MIN,
    step_min: int = STEP_MIN, horizon_h: int = HORIZON_H,
    max_results: int = MAX_ALTERNATIVES,
    history: Optional[list[BookingHistory]] = None, arena_id: int = 1,
) -> tuple[Optional[Booking], SlotCheckResult, list[datetime]]:
    """Проверяет слот, создаёт бронь и при успехе пишет событие created."""
    r = check_slot_availability(
        start, duration_min, players, game_min, game_max,
        bookings, kits, now, prep_min, arena_id=arena_id,
    )
    if not r.available:
        alt: list[datetime] = []
        if r.reason == Reason.CONFLICT:
            alt = find_alternative_slots(
                start, duration_min, players, game_min, game_max,
                bookings, kits, now, prep_min, None,
                step_min, horizon_h, max_results, arena_id,
            )
        return None, r, alt
    new_id = max((b.booking_id for b in bookings), default=0) + 1
    b = Booking(
        booking_id=new_id, client_id=client_id, game_id=game_id,
        tariff_id=tariff_id, start=start, duration_min=duration_min,
        players=players, prepaid_amount=prepaid_amount,
        status=BookingStatus.CONFIRMED, session_id=None,
        arena_id=arena_id, created_at=now,
    )
    bookings.append(b)
    record_booking_event(b, history, BookingEventType.CREATED, now,
                         None, b.start, None, b.arena_id, "оформление брони")
    return b, r, []
