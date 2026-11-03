"""Алгоритм А1 — проверка доступности слота (рис. 10, таблицы 12–14)."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from .models import (
    HORIZON_H, MAX_ALTERNATIVES, PREP_MIN, STEP_MIN,
    Booking, BookingStatus, EquipmentSet, EquipmentStatus,
    Reason, SlotCheckResult,
)


def check_slot_availability(
    start: datetime, duration_min: int, players: int,
    game_min: int, game_max: int,
    bookings: list[Booking], kits: list[EquipmentSet],
    now: datetime, prep_min: int = PREP_MIN,
    exclude_id: Optional[int] = None,
) -> SlotCheckResult:
    """А1.1. Можно ли подтвердить бронь на [start; start + duration + prep).

    Расписание не изменяется. exclude_id — бронь, которую нужно игнорировать
    (при переносе бронь не должна конфликтовать сама с собой).
    """
    # Шаг 1: корректность входных данных (D1)
    if duration_min <= 0 or players < 1 or prep_min < 0:
        return SlotCheckResult(False, Reason.INVALID_INPUT)
    # Шаг 2: число игроков в границах игры (D2)
    if players < game_min or players > game_max:
        return SlotCheckResult(False, Reason.PLAYERS_OUT_OF_RANGE)
    # Шаг 3: слот не в прошлом (D3); start == now допускается
    if start < now:
        return SlotCheckResult(False, Reason.IN_THE_PAST)
    # Шаг 4: число работоспособных комплектов (P1)
    usable = 0
    for kit in kits:
        if kit.status != EquipmentStatus.FAULTY:
            usable += 1
    # Шаг 5: хватает ли комплектов (D4)
    if usable < players:
        return SlotCheckResult(False, Reason.NOT_ENOUGH_KITS)
    # Шаг 6: занятый интервал новой брони (P2)
    new_end = start + timedelta(minutes=duration_min + prep_min)
    # Шаг 7: цикл по броням расписания (D5–D7)
    for b in bookings:
        if b.status != BookingStatus.CONFIRMED or b.booking_id == exclude_id:
            continue
        b_end = b.start + timedelta(minutes=b.duration_min + prep_min)
        # полуоткрытые интервалы: общая граница не считается пересечением
        if start < b_end and b.start < new_end:
            return SlotCheckResult(False, Reason.CONFLICT, b.booking_id)
    # Шаг 8: конфликтов нет
    return SlotCheckResult(True, Reason.OK)


def find_alternative_slots(
    start: datetime, duration_min: int, players: int,
    game_min: int, game_max: int,
    bookings: list[Booking], kits: list[EquipmentSet],
    now: datetime, prep_min: int = PREP_MIN,
    exclude_id: Optional[int] = None,
    step_min: int = STEP_MIN, horizon_h: int = HORIZON_H,
    max_results: int = MAX_ALTERNATIVES,
) -> list[datetime]:
    """А1.2. Ближайшие свободные начала после желаемого (не более max_results)."""
    result: list[datetime] = []
    t = start + timedelta(minutes=step_min)
    limit = start + timedelta(hours=horizon_h)
    while t <= limit and len(result) < max_results:
        r = check_slot_availability(t, duration_min, players, game_min, game_max,
                                    bookings, kits, now, prep_min, exclude_id)
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
) -> tuple[Optional[Booking], SlotCheckResult, list[datetime]]:
    """А1.3. Проверка и запись брони одним действием (без промежуточных вызовов)."""
    r = check_slot_availability(start, duration_min, players, game_min, game_max,
                                bookings, kits, now, prep_min)
    if not r.available:
        alt: list[datetime] = []
        if r.reason == Reason.CONFLICT:
            alt = find_alternative_slots(start, duration_min, players, game_min,
                                         game_max, bookings, kits, now, prep_min,
                                         None, step_min, horizon_h, max_results)
        return None, r, alt
    new_id = max((b.booking_id for b in bookings), default=0) + 1
    b = Booking(new_id, client_id, game_id, tariff_id, start, duration_min,
                players, prepaid_amount, BookingStatus.CONFIRMED, None)
    bookings.append(b)
    return b, r, []
