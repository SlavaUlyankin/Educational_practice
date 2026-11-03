"""Алгоритм А4 — отмена, перенос и неявка (рис. 14, таблицы 22–24)."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from .a1_slots import check_slot_availability, find_alternative_slots
from .models import (
    HORIZON_H, MAX_ALTERNATIVES, NO_SHOW_WAIT_MIN, PREP_MIN, STEP_MIN,
    Booking, BookingStatus, Code, EquipmentSet, Reason, SlotCheckResult,
)


def find_booking(bookings: list[Booking], booking_id: int) -> Optional[Booking]:
    """Поиск брони по идентификатору (линейный проход)."""
    for b in bookings:
        if b.booking_id == booking_id:
            return b
    return None


def cancel_booking(bookings: list[Booking], booking_id: int,
                   now: datetime) -> tuple[Code, Optional[float]]:
    """А4.1. Отмена: бронь перестаёт занимать слот. Возвращает сумму предоплаты."""
    b = find_booking(bookings, booking_id)
    if b is None:
        return Code.NOT_FOUND, None
    if b.status != BookingStatus.CONFIRMED or b.session_id is not None:
        return Code.INVALID_STATE, None
    if now >= b.start:
        return Code.TOO_LATE, None
    b.status = BookingStatus.CANCELLED
    return Code.OK, b.prepaid_amount


def reschedule_booking(
    bookings: list[Booking], booking_id: int, new_start: datetime,
    kits: list[EquipmentSet], game_min: int, game_max: int, now: datetime,
    prep_min: int = PREP_MIN, step_min: int = STEP_MIN,
    horizon_h: int = HORIZON_H, max_results: int = MAX_ALTERNATIVES,
) -> tuple[Code, Optional[SlotCheckResult], list[datetime]]:
    """А4.2. Перенос только на свободный слот; при отказе бронь не меняется."""
    b = find_booking(bookings, booking_id)                          # P1
    if b is None:                                                   # D1
        return Code.NOT_FOUND, None, []
    if b.status != BookingStatus.CONFIRMED or b.session_id is not None:  # D2
        return Code.INVALID_STATE, None, []
    if now >= b.start:                                              # D3
        return Code.TOO_LATE, None, []
    # P2: та же проверка, что при бронировании; своя бронь исключается
    r = check_slot_availability(new_start, b.duration_min, b.players, game_min,
                                game_max, bookings, kits, now, prep_min,
                                b.booking_id)
    if not r.available:                                             # D4
        alt: list[datetime] = []
        if r.reason == Reason.CONFLICT:                             # D5
            alt = find_alternative_slots(new_start, b.duration_min, b.players,
                                         game_min, game_max, bookings, kits, now,
                                         prep_min, b.booking_id, step_min,
                                         horizon_h, max_results)
        return Code.SLOT_UNAVAILABLE, r, alt
    b.start = new_start                                             # P5
    return Code.OK, r, []


def mark_no_show(bookings: list[Booking], booking_id: int, now: datetime,
                 wait_min: int = NO_SHOW_WAIT_MIN) -> Code:
    """А4.3. Фиксация неявки не раньше окончания срока ожидания."""
    b = find_booking(bookings, booking_id)
    if b is None:
        return Code.NOT_FOUND
    if b.status != BookingStatus.CONFIRMED or b.session_id is not None:
        return Code.INVALID_STATE
    if now < b.start + timedelta(minutes=wait_min):
        return Code.TOO_EARLY
    b.status = BookingStatus.NO_SHOW
    return Code.OK
