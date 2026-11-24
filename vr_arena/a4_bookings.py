"""Алгоритм А5 — отмена, перенос и неявка с историей изменений брони."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from .a1_slots import (
    record_booking_event, check_slot_availability, find_alternative_slots,
)
from .models import (
    HORIZON_H, MAX_ALTERNATIVES, NO_SHOW_WAIT_MIN, PREP_MIN, STEP_MIN,
    Booking, BookingEventType, BookingHistory, BookingStatus, Code,
    EquipmentSet, Reason, SlotCheckResult,
)


def find_booking(bookings: list[Booking], booking_id: int) -> Optional[Booking]:
    for b in bookings:
        if b.booking_id == booking_id:
            return b
    return None


def cancel_booking(
    bookings: list[Booking], booking_id: int, now: datetime,
    history: Optional[list[BookingHistory]] = None,
    reason: Optional[str] = None,
) -> tuple[Code, Optional[float]]:
    """Отменяет активную бронь и при успехе пишет событие cancelled."""
    b = find_booking(bookings, booking_id)
    if b is None:
        return Code.NOT_FOUND, None
    if b.status != BookingStatus.CONFIRMED or b.session_id is not None:
        return Code.INVALID_STATE, None
    if now >= b.start:
        return Code.TOO_LATE, None
    b.status = BookingStatus.CANCELLED
    record_booking_event(b, history, BookingEventType.CANCELLED, now,
                         b.start, None, b.arena_id, None, reason or "отмена по запросу клиента")
    return Code.OK, b.prepaid_amount


def reschedule_booking(
    bookings: list[Booking], booking_id: int, new_start: datetime,
    kits: list[EquipmentSet], game_min: int, game_max: int, now: datetime,
    prep_min: int = PREP_MIN, step_min: int = STEP_MIN,
    horizon_h: int = HORIZON_H, max_results: int = MAX_ALTERNATIVES,
    history: Optional[list[BookingHistory]] = None,
    new_arena_id: Optional[int] = None, reason: Optional[str] = None,
) -> tuple[Code, Optional[SlotCheckResult], list[datetime]]:
    """Переносит время и, при необходимости, арену; отказ не создаёт истории."""
    b = find_booking(bookings, booking_id)
    if b is None:
        return Code.NOT_FOUND, None, []
    if b.status != BookingStatus.CONFIRMED or b.session_id is not None:
        return Code.INVALID_STATE, None, []
    if now >= b.start:
        return Code.TOO_LATE, None, []
    target_arena = b.arena_id if new_arena_id is None else new_arena_id
    r = check_slot_availability(
        new_start, b.duration_min, b.players, game_min, game_max,
        bookings, kits, now, prep_min, b.booking_id, target_arena,
    )
    if not r.available:
        alt: list[datetime] = []
        if r.reason == Reason.CONFLICT:
            alt = find_alternative_slots(
                new_start, b.duration_min, b.players, game_min, game_max,
                bookings, kits, now, prep_min, b.booking_id,
                step_min, horizon_h, max_results, target_arena,
            )
        return Code.SLOT_UNAVAILABLE, r, alt
    old_start, old_arena = b.start, b.arena_id
    b.start, b.arena_id = new_start, target_arena
    record_booking_event(b, history, BookingEventType.RESCHEDULED, now,
                         old_start, b.start, old_arena, b.arena_id,
                         reason or "перенос по запросу клиента")
    return Code.OK, r, []


def mark_no_show(
    bookings: list[Booking], booking_id: int, now: datetime,
    wait_min: int = NO_SHOW_WAIT_MIN,
    history: Optional[list[BookingHistory]] = None,
    reason: Optional[str] = None,
) -> Code:
    """Фиксирует неявку не раньше окончания ожидания и пишет событие no_show."""
    b = find_booking(bookings, booking_id)
    if b is None:
        return Code.NOT_FOUND
    if b.status != BookingStatus.CONFIRMED or b.session_id is not None:
        return Code.INVALID_STATE
    if now < b.start + timedelta(minutes=wait_min):
        return Code.TOO_EARLY
    b.status = BookingStatus.NO_SHOW
    record_booking_event(b, history, BookingEventType.NO_SHOW, now,
                         b.start, None, b.arena_id, None, reason or "истёк срок ожидания группы")
    return Code.OK
