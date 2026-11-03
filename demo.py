"""Демонстрационный сценарий: один рабочий день VR-арены (данные вымышленные)."""
from datetime import datetime

from vr_arena.a1_slots import create_booking
from vr_arena.a2_session_time import (
    finish_session, session_time_state, start_session)
from vr_arena.a3_equipment import (
    change_status, issue_equipment, replace_equipment, return_equipment)
from vr_arena.a4_bookings import cancel_booking, mark_no_show, reschedule_booking
from vr_arena.models import (
    Booking, EquipmentSet, EquipmentStatus, Session, SessionEquipment, StatusLogEntry)


def t(h: int, m: int = 0) -> datetime:
    return datetime(2026, 11, 10, h, m)


def show(bookings):
    for b in sorted(bookings, key=lambda x: x.start):
        end = b.start.strftime("%H:%M")
        print(f"   бронь {b.booking_id}: {end}, {b.duration_min} мин, "
              f"{b.players} игр., статус {b.status.value}")


GMIN, GMAX = 2, 6                       # игра допускает 2–6 игроков
now = t(12)
kits = [EquipmentSet(i, f"SET-{i:02d}") for i in range(1, 9)]
bookings: list[Booking] = []
rows: list[SessionEquipment] = []
log: list[StatusLogEntry] = []

print("1. Бронирование (А1)")
for client, start, dur, pl in [(101, t(18), 60, 4), (102, t(19), 30, 3),
                               (103, t(19, 15), 45, 5), (104, t(20, 30), 45, 6)]:
    b, r, alt = create_booking(client, 1, 3, start, dur, pl, 0.0, GMIN, GMAX,
                               bookings, kits, now)
    if b:
        print(f"   клиент {client}, {start:%H:%M}, {dur} мин: бронь {b.booking_id} подтверждена")
    else:
        print(f"   клиент {client}, {start:%H:%M}, {dur} мин: отказ {r.reason.value} "
              f"(бронь {r.conflict_booking_id}); альтернативы: "
              + ", ".join(a.strftime("%H:%M") for a in alt))
show(bookings)

print("\n2. Перенос и отмена (А4)")
code, r, alt = reschedule_booking(bookings, 3, t(19, 30), kits, GMIN, GMAX, now)
print(f"   перенос брони 3 (20:30) на 19:30 -> {code.value}, причина {r.reason.value} "
      f"(бронь {r.conflict_booking_id})")
code, amount = cancel_booking(bookings, 2, now)
print(f"   отмена брони 2 -> {code.value}, предоплата {amount}")
code, r, alt = reschedule_booking(bookings, 3, t(19, 30), kits, GMIN, GMAX, now)
print(f"   повторный перенос брони 3 на 19:30 -> {code.value}")
show(bookings)

print("\n3. Сеанс брони 1: выдача оборудования (А3), старт (А2)")
session = Session(1, players_count=4, duration_min=60)
bookings[0].session_id = session.session_id
code, ids, _ = issue_equipment(session, kits, rows, t(17, 55), log)
print(f"   выдача: {code.value}, комплекты {ids}")
code, planned_end = start_session(session, t(18, 2))
print(f"   старт: {code.value}, плановое окончание {planned_end:%H:%M}")
code, new_id = replace_equipment(session, 2, kits, rows, t(18, 20), log)
print(f"   18:20 неисправность SET-02: замена {code.value}, выдан комплект {new_id}")
for moment in (t(18, 30), t(19, 0), t(19, 4), t(19, 9)):
    s = session_time_state(session, moment, 5)
    print(f"   {moment:%H:%M}: {s.state.value}, осталось {s.remaining_min} мин, "
          f"превышение {s.overtime_min} мин")

print("\n4. Завершение, возврат, подготовка (А2, А3)")
code, rep = finish_session(session, bookings, t(19, 9))
print(f"   завершение: {code.value}, фактически {rep.actual_min} мин, превышение {rep.overtime_min} мин")
conds = {1: "ok", 3: "ok", 4: "damaged", 5: "ok"}
code, ids = return_equipment(session, rows, kits, t(19, 10), conds, log)
print(f"   возврат: {code.value}, комплекты {ids}")
for k in kits:
    if k.status == EquipmentStatus.RETURNED_PENDING:
        change_status(k, EquipmentStatus.SERVICING, t(19, 20), "дезинфекция, зарядка", log)
        change_status(k, EquipmentStatus.AVAILABLE, t(19, 40), "готов", log)
print("   статусы комплектов:", ", ".join(f"{k.inventory_code}={k.status.value}" for k in kits))

print("\n5. Неявка (А4)")
code = mark_no_show(bookings, 3, t(19, 44), 15)
print(f"   бронь 3 (19:30), проверка в 19:44 -> {code.value}")
code = mark_no_show(bookings, 3, t(19, 45), 15)
print(f"   бронь 3 (19:30), проверка в 19:45 -> {code.value}")
show(bookings)
print(f"\nЗаписей в журнале статусов: {len(log)}")
