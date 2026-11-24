"""Проверки сущностей arena и booking_history, добавленных на этапе 4.1."""
from __future__ import annotations

from collections import namedtuple
from datetime import datetime

from vr_arena.a1_slots import check_slot_availability, create_booking
from vr_arena.a4_bookings import cancel_booking, mark_no_show, reschedule_booking
from vr_arena.models import EquipmentSet

Case = namedtuple("Case", "id desc expected run")
NOW = datetime(2026, 11, 10, 12, 0)
GMIN, GMAX = 2, 6


def D(h: int, m: int = 0) -> datetime:
    return datetime(2026, 11, 10, h, m)


def kits(arena_id: int = 1, n: int = 8) -> list[EquipmentSet]:
    return [EquipmentSet(i, f"SET-{i:02d}", arena_id=arena_id) for i in range(1, n + 1)]


def new_booking(history):
    bookings = []
    b, result, _ = create_booking(
        101, 1, 3, D(18), 60, 4, 1000.0, GMIN, GMAX,
        bookings, kits(), NOW, history=history,
    )
    return bookings, b, result


def _er_1():
    history = []
    bookings, b, result = new_booking(history)
    e = history[-1]
    return (f"{result.reason.value}|events={len(history)}|type={e.event_type.value}"
            f"|old={e.old_start_time}|new={e.new_start_time:%H:%M}"
            f"|arena={e.new_arena_id}|created_at={b.created_at:%H:%M}")


def _er_2():
    history = []
    bookings, b, _ = new_booking(history)
    code, _, _ = reschedule_booking(
        bookings, b.booking_id, D(20), kits(), GMIN, GMAX, NOW, history=history,
    )
    e = history[-1]
    return (f"{code.value}|events={len(history)}|type={e.event_type.value}"
            f"|old={e.old_start_time:%H:%M}|new={e.new_start_time:%H:%M}")


def _er_3():
    history = []
    bookings, b, _ = new_booking(history)
    code, _ = cancel_booking(bookings, b.booking_id, D(13), history)
    e = history[-1]
    return (f"{code.value}|type={e.event_type.value}|old={e.old_start_time:%H:%M}"
            f"|new={e.new_start_time}|arena={e.old_arena_id}")


def _er_4():
    history = []
    bookings, b, _ = new_booking(history)
    code = mark_no_show(bookings, b.booking_id, D(18, 15), 15, history)
    e = history[-1]
    return f"{code.value}|type={e.event_type.value}|old={e.old_start_time:%H:%M}|new={e.new_start_time}"


def _er_5():
    bookings, _, _ = new_booking([])
    result = check_slot_availability(
        D(18), 60, 4, GMIN, GMAX, bookings, kits(arena_id=2), NOW, arena_id=2,
    )
    return result.reason.value


def _er_6():
    mixed_kits = kits(arena_id=1, n=3) + kits(arena_id=2, n=5)
    result = check_slot_availability(
        D(18), 60, 4, GMIN, GMAX, [], mixed_kits, NOW, arena_id=1,
    )
    return result.reason.value


def _er_7():
    history = []
    bookings, b, _ = new_booking(history)
    other, _, _ = create_booking(
        102, 1, 3, D(20), 45, 4, 0.0, GMIN, GMAX,
        bookings, kits(), NOW,
    )
    history_before = len(history)
    code, result, _ = reschedule_booking(
        bookings, b.booking_id, D(19, 30), kits(), GMIN, GMAX, NOW, history=history,
    )
    return (f"{code.value}|{result.reason.value}(id={result.conflict_booking_id})"
            f"|start={b.start:%H:%M}|new_events={len(history) - history_before}")


def _er_8():
    history = []
    bookings, b, _ = new_booking(history)
    code, _, _ = reschedule_booking(
        bookings, b.booking_id, D(20), kits(arena_id=2), GMIN, GMAX, NOW,
        history=history, new_arena_id=2,
    )
    e = history[-1]
    old_slot = check_slot_availability(
        D(18), 60, 4, GMIN, GMAX, bookings, kits(), NOW, arena_id=1,
    )
    new_slot = check_slot_availability(
        D(20), 60, 4, GMIN, GMAX, bookings, kits(arena_id=2), NOW, arena_id=2,
    )
    return (f"{code.value}|arena={b.arena_id}|old={e.old_start_time:%H:%M}"
            f"|new={e.new_start_time:%H:%M}|old_arena={e.old_arena_id}"
            f"|new_arena={e.new_arena_id}|old_slot={old_slot.reason.value}"
            f"|new_slot={new_slot.reason.value}(id={new_slot.conflict_booking_id})")


ER_CASES = [
    Case("ER-1", "Создание брони фиксирует новое время, арену и момент создания",
         "OK|events=1|type=created|old=None|new=18:00|arena=1|created_at=12:00", _er_1),
    Case("ER-2", "Перенос сохраняет прежнее и новое время",
         "OK|events=2|type=rescheduled|old=18:00|new=20:00", _er_2),
    Case("ER-3", "Отмена сохраняет прежний слот и не создаёт новый",
         "OK|type=cancelled|old=18:00|new=None|arena=1", _er_3),
    Case("ER-4", "Неявка фиксируется в истории брони",
         "OK|type=no_show|old=18:00|new=None", _er_4),
    Case("ER-5", "Одинаковый слот на разных аренах не является конфликтом", "OK", _er_5),
    Case("ER-6", "Комплекты другой арены не учитываются при проверке", "NOT_ENOUGH_KITS", _er_6),
    Case("ER-7", "Неуспешный перенос не меняет бронь и не создаёт событие",
         "SLOT_UNAVAILABLE|CONFLICT(id=2)|start=18:00|new_events=0", _er_7),
    Case("ER-8", "Перенос на другую арену сохраняет прежнюю и новую арену",
         "OK|arena=2|old=18:00|new=20:00|old_arena=1|new_arena=2"
         "|old_slot=OK|new_slot=CONFLICT(id=1)", _er_8),
]
