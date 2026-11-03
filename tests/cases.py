"""Тест-кейсы А1–А4: одна таблица данных для unittest и для печати «ожидалось / получено».

Ожидаемые результаты заданы вручную по таблицам 14, 17, 21, 24 отчёта,
а не получены запуском кода.
"""
from __future__ import annotations

from collections import namedtuple
from datetime import datetime

from vr_arena.a1_slots import check_slot_availability, create_booking, find_alternative_slots
from vr_arena.a2_session_time import (
    finish_session, session_time_state, sessions_needing_attention, start_session)
from vr_arena.a3_equipment import (
    change_status, issue_equipment, replace_equipment, return_equipment, select_available)
from vr_arena.a4_bookings import cancel_booking, mark_no_show, reschedule_booking
from vr_arena.models import (
    Booking, BookingStatus, Code, EquipmentSet, EquipmentStatus as ES, Session,
    SessionEquipment, SessionStatus as SS)

Case = namedtuple("Case", "id desc expected run")

NOW = datetime(2026, 11, 10, 12, 0)
GMIN, GMAX = 2, 6          # границы числа игроков игры


def D(h: int, m: int = 0) -> datetime:
    return datetime(2026, 11, 10, h, m)


def hhmm(ts) -> str:
    return ",".join(t.strftime("%H:%M") for t in ts)


def kits(n: int = 8) -> list[EquipmentSet]:
    return [EquipmentSet(i, f"SET-{i:02d}") for i in range(1, n + 1)]


def b1() -> Booking:   # 18:00, 60 мин -> занимает [18:00; 19:10)
    return Booking(1, 101, 1, 3, D(18), 60, 4, 1000.0)


def b2() -> Booking:   # 20:00, 45 мин -> занимает [20:00; 20:55)
    return Booking(2, 102, 1, 2, D(20), 45, 4, 0.0)


def chk(start, dur, pl, bookings, kit_list=None, now=NOW, exclude=None) -> str:
    r = check_slot_availability(start, dur, pl, GMIN, GMAX, bookings,
                                kit_list if kit_list is not None else kits(), now,
                                10, exclude)
    return r.reason.value + (f"(id={r.conflict_booking_id})" if r.conflict_booking_id else "")


# ------------------------------ А1 (таблица 14) ------------------------------
def _a1_6():
    b = b1(); b.status = BookingStatus.CANCELLED
    return chk(D(18), 60, 4, [b])

def _a1_7():
    ks = kits(); [setattr(k, "status", ES.FAULTY) for k in ks[:5]]
    return chk(D(20), 60, 4, [b1()], ks)

def _a1_12():
    return hhmm(find_alternative_slots(D(18), 60, 4, GMIN, GMAX, [b1()], kits(), NOW))

def _a1_13():
    bs = [b1()]
    b, r, alt = create_booking(103, 1, 2, D(20), 45, 4, 0.0, GMIN, GMAX, bs, kits(), NOW)
    return f"{r.reason.value}|id={b.booking_id}|n={len(bs)}|status={b.status.value}"

def _a1_14():
    bs = [b1()]
    b, r, alt = create_booking(103, 1, 3, D(18), 60, 4, 0.0, GMIN, GMAX, bs, kits(), NOW)
    return f"{r.reason.value}(id={r.conflict_booking_id})|booking={b}|alt={hhmm(alt)}|n={len(bs)}"

def _a1_15():
    bs = []
    args = (GMIN, GMAX, bs, kits(), NOW)
    b_1, r1, _ = create_booking(101, 1, 3, D(18), 60, 4, 0.0, *args)
    b_2, r2, _ = create_booking(102, 1, 3, D(18), 60, 4, 0.0, *args)
    return f"{r1.reason.value}|{r2.reason.value}(id={r2.conflict_booking_id})|n={len(bs)}"

A1_CASES = [
    Case("A1-1", "Пустое расписание", "OK", lambda: chk(D(18), 60, 4, [])),
    Case("A1-2", "Касание границей: 19:10, 30 мин (B1 занимает до 19:10)", "OK",
         lambda: chk(D(19, 10), 30, 4, [b1()])),
    Case("A1-3", "Нарушен интервал на подготовку: 19:00, 30 мин", "CONFLICT(id=1)",
         lambda: chk(D(19), 30, 4, [b1()])),
    Case("A1-4", "Частичное пересечение слева: 17:30, 45 мин", "CONFLICT(id=1)",
         lambda: chk(D(17, 30), 45, 4, [b1()])),
    Case("A1-5", "Полное вложение: 18:15, 30 мин", "CONFLICT(id=1)",
         lambda: chk(D(18, 15), 30, 4, [b1()])),
    Case("A1-6", "Отменённая бронь не блокирует слот", "OK", _a1_6),
    Case("A1-7", "Нехватка комплектов (работоспособных 3, игроков 4)", "NOT_ENOUGH_KITS", _a1_7),
    Case("A1-8", "Нулевая длительность", "INVALID_INPUT", lambda: chk(D(20), 0, 4, [b1()])),
    Case("A1-9", "Число игроков вне границ игры (7 при максимуме 6)", "PLAYERS_OUT_OF_RANGE",
         lambda: chk(D(20), 60, 7, [b1()])),
    Case("A1-10", "Слот в прошлом", "IN_THE_PAST", lambda: chk(D(11), 60, 4, [b1()])),
    Case("A1-11", "Перенос на собственный интервал (exclude_id = 1)", "OK",
         lambda: chk(D(18), 60, 4, [b1()], exclude=1)),
    Case("A1-12", "Альтернативы при конфликте с B1", "19:15,19:30,19:45", _a1_12),
    Case("A1-13", "create_booking: свободный слот, бронь записана", "OK|id=2|n=2|status=confirmed", _a1_13),
    Case("A1-14", "create_booking: конфликт, брони нет, расписание не изменено",
         "CONFLICT(id=1)|booking=None|alt=19:15,19:30,19:45|n=1", _a1_14),
    Case("A1-15", "Две заявки на один слот подряд: вторая отклонена",
         "OK|CONFLICT(id=1)|n=1", _a1_15),
    Case("A1-16", "Начало ровно в now допускается", "OK", lambda: chk(NOW, 60, 4, [])),
]


# ------------------------------ А2 (таблица 17) ------------------------------
def running() -> Session:
    return Session(1, 4, 60, SS.IN_PROGRESS, started_at=D(18))

def st(session, now) -> str:
    r = session_time_state(session, now, 5)
    return f"{r.state.value}(rem={r.remaining_min},over={r.overtime_min})"

def _a2_8():
    s = Session(1, 4, 0); code, _ = start_session(s, D(18))
    return f"{code.value}|status={s.status.value}|started={s.started_at}"

def _a2_9():
    s = Session(1, 4, 60); code, pe = start_session(s, D(18))
    return f"{code.value}|planned_end={pe.strftime('%H:%M')}|status={s.status.value}"

def _a2_10():
    s = running(); code, _ = start_session(s, D(18, 30))
    return f"{code.value}|started={s.started_at.strftime('%H:%M')}"

def _a2_11():
    s = running()
    bs = [Booking(1, 101, 1, 3, D(18), 60, 4, session_id=1),
          Booking(2, 102, 1, 3, D(18), 60, 4, status=BookingStatus.CANCELLED, session_id=1)]
    code, rep = finish_session(s, bs, D(19, 12))
    return (f"{code.value}|actual={rep.actual_min}|over={rep.overtime_min}"
            f"|b1={bs[0].status.value}|b2={bs[1].status.value}|status={s.status.value}")

def _a2_12():
    s = running(); code, rep = finish_session(s, [], D(18))
    return f"{code.value}|status={s.status.value}"

def _a2_13():
    s = Session(1, 4, 60, SS.COMPLETED, D(18), D(19)); code, _ = finish_session(s, [], D(19, 30))
    return code.value

def _a2_14():
    s = running(); code, rep = finish_session(s, [], D(19, 0))
    return f"{code.value}|actual={rep.actual_min}|over={rep.overtime_min}"

def _a2_15():
    s1 = Session(1, 4, 60, SS.IN_PROGRESS, D(18))
    s2 = Session(2, 4, 60, SS.COMPLETED, D(16), D(17))
    s3 = Session(3, 4, 60, SS.PREPARED)
    res = sessions_needing_attention([s1, s2, s3], D(18, 57), 5)
    return ";".join(f"{i}:{r.state.value}" for i, r in res)

def _a2_16():
    s1 = Session(1, 4, 60, SS.IN_PROGRESS, D(18))
    res = sessions_needing_attention([s1], D(19, 3), 5)
    return ";".join(f"{i}:{r.state.value}({r.overtime_min})" for i, r in res)

A2_CASES = [
    Case("A2-1", "Обычный ход: 18:30", "RUNNING(rem=30,over=0)", lambda: st(running(), D(18, 30))),
    Case("A2-2", "Порог warn_min: 18:55", "ENDING_SOON(rem=5,over=0)", lambda: st(running(), D(18, 55))),
    Case("A2-3", "Касание планового окончания: 19:00", "TIME_UP(rem=0,over=0)", lambda: st(running(), D(19))),
    Case("A2-4", "Превышение на 7 минут: 19:07", "TIME_UP(rem=0,over=7)", lambda: st(running(), D(19, 7))),
    Case("A2-5", "Сеанс не начат", "NOT_STARTED(rem=0,over=0)", lambda: st(Session(1, 4, 60), D(18))),
    Case("A2-6", "Сеанс завершён", "COMPLETED(rem=0,over=0)",
         lambda: st(Session(1, 4, 60, SS.COMPLETED, D(18), D(19)), D(19, 5))),
    Case("A2-7", "Время раньше начала: 17:59", "INVALID_TIME(rem=0,over=0)", lambda: st(running(), D(17, 59))),
    Case("A2-8", "Старт с нулевой длительностью", "INVALID_DURATION|status=prepared|started=None", _a2_8),
    Case("A2-9", "Корректный старт", "OK|planned_end=19:00|status=in_progress", _a2_9),
    Case("A2-10", "Повторный старт", "INVALID_STATE|started=18:00", _a2_10),
    Case("A2-11", "Завершение с превышением; отменённая бронь не меняется",
         "OK|actual=72|over=12|b1=completed|b2=cancelled|status=completed", _a2_11),
    Case("A2-12", "Завершение в момент старта", "INVALID_TIME|status=in_progress", _a2_12),
    Case("A2-13", "Повторное завершение", "INVALID_STATE", _a2_13),
    Case("A2-14", "Завершение при пустом расписании, ровно в плановое время", "OK|actual=60|over=0", _a2_14),
    Case("A2-15", "Выбор сеансов, требующих внимания (18:57)", "1:ENDING_SOON", _a2_15),
    Case("A2-16", "Выбор сеансов: превышение на 3 мин (19:03)", "1:TIME_UP(3)", _a2_16),
    Case("A2-17", "За пределами порога: 18:54", "RUNNING(rem=6,over=0)", lambda: st(running(), D(18, 54))),
]


# ------------------------------ А3 (таблица 21) ------------------------------
def kit_with(status: ES) -> EquipmentSet:
    return EquipmentSet(1, "SET-01", status=status)

def cs(kit, new) -> str:
    log = []
    code, old = change_status(kit, new, D(12), None, log)
    return f"{code.value}|status={kit.status.value}|log={len(log)}"

def _a3_8():
    ks = kits(); [setattr(k, "status", ES.FAULTY) for k in ks[3:]]
    code, sel, sh = select_available(ks, 4)
    return f"{code.value}|{len(sel)}|shortage={sh}"

def _a3_7():
    code, sel, sh = select_available(kits(), 4)
    return f"{code.value}|{len(sel)}|shortage={sh}|ids={','.join(str(k.equipment_id) for k in sel)}"

def _a3_9():
    code, sel, sh = select_available(kits(), 0)
    return code.value

def prep_session(players=4, status=SS.PREPARED) -> Session:
    return Session(1, players, 60, status)

def _a3_10():
    ks, rows, log, s = kits(), [], [], prep_session()
    code, ids, sh = issue_equipment(s, ks, rows, D(17, 55), log)
    st_ = ",".join(k.status.value for k in ks[:4])
    return f"{code.value}|ids={ids}|{st_}|rows={len(rows)}|log={len(log)}"

def _a3_11():
    ks = kits(); [setattr(k, "status", ES.FAULTY) for k in ks[3:]]
    rows, log, s = [], [], prep_session()
    code, ids, sh = issue_equipment(s, ks, rows, D(17, 55), log)
    issued = sum(k.status == ES.ISSUED for k in ks)
    return f"{code.value}|shortage={sh}|issued={issued}|rows={len(rows)}|log={len(log)}"

def _a3_12():
    ks, rows, log, s = kits(), [], [], prep_session()
    issue_equipment(s, ks, rows, D(17, 55), log)
    code, ids, sh = issue_equipment(s, ks, rows, D(17, 56), log)
    return f"{code.value}|rows={len(rows)}|log={len(log)}"

def _a3_13():
    code, ids, sh = issue_equipment(prep_session(status=SS.IN_PROGRESS), kits(), [], D(18), [])
    return code.value

def issued_world(players=2):
    """Сеанс завершён, комплекты 1..players выданы."""
    ks, rows, log = kits(), [], []
    s = prep_session(players)
    issue_equipment(s, ks, rows, D(17, 55), log)
    s.status = SS.COMPLETED
    return s, ks, rows, log

def _a3_14():
    s, ks, rows, log = issued_world(2)
    code, ids = return_equipment(s, rows, ks, D(19, 10), {1: "ok", 2: "ok"}, log)
    return (f"{code.value}|{ks[0].status.value},{ks[1].status.value}"
            f"|closed={sum(r.returned_at is not None for r in rows)}")

def _a3_15():
    s, ks, rows, log = issued_world(2)
    code, ids = return_equipment(s, rows, ks, D(19, 10), {1: "ok", 2: "damaged"}, log)
    return f"{code.value}|{ks[0].status.value},{ks[1].status.value}"

def _a3_16():
    s, ks, rows, log = issued_world(2)
    ks[0].status = ES.FAULTY            # отмечен неисправным во время сеанса
    n = len(log)
    code, ids = return_equipment(s, rows, ks, D(19, 10), {1: "damaged", 2: "ok"}, log)
    return (f"{code.value}|{ks[0].status.value},{ks[1].status.value}"
            f"|new_log={len(log) - n}|closed={sum(r.returned_at is not None for r in rows)}")

def _a3_17():
    s, ks, rows, log = issued_world(2)
    code, ids = return_equipment(s, rows, ks, D(19, 10), {1: "ok"}, log)
    return (f"{code.value}|{ks[0].status.value},{ks[1].status.value}"
            f"|closed={sum(r.returned_at is not None for r in rows)}")

def _a3_18():
    s, ks, rows, log = issued_world(2)
    ks[0].status = ES.FAULTY
    code, ids = return_equipment(s, rows, ks, D(19, 10), {1: "ok", 2: "ok"}, log)
    return (f"{code.value}|{ks[0].status.value},{ks[1].status.value}"
            f"|closed={sum(r.returned_at is not None for r in rows)}")

def _a3_19():
    s, ks, rows, log = issued_world(2)
    s.status = SS.IN_PROGRESS
    code, ids = return_equipment(s, rows, ks, D(19, 10), {1: "ok", 2: "ok"}, log)
    return code.value

def _a3_20():
    code, ids = return_equipment(prep_session(status=SS.COMPLETED), [], kits(), D(19), {}, [])
    return code.value

def running_world(players=4, fleet=8):
    ks, rows, log = kits(fleet), [], []
    s = prep_session(players)
    issue_equipment(s, ks, rows, D(17, 55), log)
    s.status = SS.IN_PROGRESS
    return s, ks, rows, log

def _a3_21():
    s, ks, rows, log = running_world(4, 8)
    code, new_id = replace_equipment(s, 1, ks, rows, D(18, 20), log)
    return (f"{code.value}|new={new_id}|SET-01={ks[0].status.value}|SET-05={ks[4].status.value}"
            f"|rows={len(rows)}|row1={rows[0].return_condition}")

def _a3_22():
    s, ks, rows, log = running_world(4, 4)
    code, new_id = replace_equipment(s, 1, ks, rows, D(18, 20), log)
    return f"{code.value}|SET-01={ks[0].status.value}|row1_closed={rows[0].returned_at is not None}|rows={len(rows)}"

def _a3_23():
    s, ks, rows, log = running_world(4, 8)
    code, new_id = replace_equipment(s, 7, ks, rows, D(18, 20), log)
    return f"{code.value}|SET-07={ks[6].status.value}"

def _a3_24():
    ks = kits(); k = ks[0]; k.status = ES.RETURNED_PENDING; log = []
    c1, _ = change_status(k, ES.SERVICING, D(19, 20), "дезинфекция, зарядка", log)
    c2, _ = change_status(k, ES.AVAILABLE, D(19, 40), "заряд достаточен", log)
    return f"{c1.value},{c2.value}|{k.status.value}|log={len(log)}"

A3_CASES = [
    Case("A3-1", "available -> issued", "OK|status=issued|log=1", lambda: cs(kit_with(ES.AVAILABLE), ES.ISSUED)),
    Case("A3-2", "issued -> available (минуя обработку)", "INVALID_TRANSITION|status=issued|log=0",
         lambda: cs(kit_with(ES.ISSUED), ES.AVAILABLE)),
    Case("A3-3", "faulty -> available", "INVALID_TRANSITION|status=faulty|log=0",
         lambda: cs(kit_with(ES.FAULTY), ES.AVAILABLE)),
    Case("A3-4", "faulty -> servicing", "OK|status=servicing|log=1", lambda: cs(kit_with(ES.FAULTY), ES.SERVICING)),
    Case("A3-5", "Тот же статус: available -> available", "INVALID_TRANSITION|status=available|log=0",
         lambda: cs(kit_with(ES.AVAILABLE), ES.AVAILABLE)),
    Case("A3-6", "Неизвестный статус «broken»", "UNKNOWN_STATUS|status=available|log=0",
         lambda: cs(kit_with(ES.AVAILABLE), "broken")),
    Case("A3-7", "Подбор: 4 игрока, доступно 8", "OK|4|shortage=0|ids=1,2,3,4", _a3_7),
    Case("A3-8", "Подбор: 4 игрока, доступно 3", "NOT_ENOUGH_AVAILABLE|3|shortage=1", _a3_8),
    Case("A3-9", "Подбор: нулевое число игроков", "INVALID_INPUT", _a3_9),
    Case("A3-10", "Выдача 4 комплектов сеансу в статусе prepared",
         "OK|ids=[1, 2, 3, 4]|issued,issued,issued,issued|rows=4|log=4", _a3_10),
    Case("A3-11", "Выдача при нехватке: данные не изменились",
         "NOT_ENOUGH_AVAILABLE|shortage=1|issued=0|rows=0|log=0", _a3_11),
    Case("A3-12", "Повторная выдача тому же сеансу", "ALREADY_ISSUED|rows=4|log=4", _a3_12),
    Case("A3-13", "Выдача сеансу в статусе in_progress", "INVALID_STATE", _a3_13),
    Case("A3-14", "Возврат: оба комплекта исправны", "OK|returned_pending,returned_pending|closed=2", _a3_14),
    Case("A3-15", "Возврат: один комплект повреждён", "OK|returned_pending,faulty", _a3_15),
    Case("A3-16", "Возврат: комплект уже faulty (отмечен во время сеанса)",
         "OK|faulty,returned_pending|new_log=1|closed=2", _a3_16),
    Case("A3-17", "Возврат: нет состояния для одного комплекта — без изменений",
         "MISSING_CONDITION|issued,issued|closed=0", _a3_17),
    Case("A3-18", "Возврат: faulty при состоянии ok — без изменений",
         "INCONSISTENT_STATE|faulty,issued|closed=0", _a3_18),
    Case("A3-19", "Возврат при незавершённом сеансе", "INVALID_STATE", _a3_19),
    Case("A3-20", "Возврат: у сеанса нет активных строк", "NO_ACTIVE_ISSUE", _a3_20),
    Case("A3-21", "Замена комплекта при наличии резерва",
         "OK|new=5|SET-01=faulty|SET-05=issued|rows=5|row1=damaged", _a3_21),
    Case("A3-22", "Замена без резерва: неисправность записана",
         "NO_REPLACEMENT|SET-01=faulty|row1_closed=True|rows=4", _a3_22),
    Case("A3-23", "Замена комплекта, не выданного сеансу", "NOT_ISSUED|SET-07=available", _a3_23),
    Case("A3-24", "Цепочка обработки: returned_pending -> servicing -> available",
         "OK,OK|available|log=2", _a3_24),
]


# ------------------------------ А4 (таблица 24) ------------------------------
def world():
    return [b1(), b2()], kits()

def _a4_1():
    bs, ks = world()
    code, amount = cancel_booking(bs, 1, NOW)
    return f"{code.value}|{amount}|{bs[0].status.value}|recheck={chk(D(18), 60, 4, bs, ks)}"

def _a4_2():
    bs, ks = world(); code, _ = cancel_booking(bs, 1, D(18))
    return f"{code.value}|{bs[0].status.value}"

def _a4_3():
    bs, ks = world(); bs[0].status = BookingStatus.CANCELLED
    return cancel_booking(bs, 1, NOW)[0].value

def _a4_4():
    bs, ks = world(); bs[0].session_id = 1
    return cancel_booking(bs, 1, NOW)[0].value

def _a4_5():
    bs, ks = world(); return cancel_booking(bs, 99, NOW)[0].value

def _a4_6():
    return cancel_booking([], 1, NOW)[0].value

def rs(bs, ks, new_start, now=NOW, bid=1):
    code, r, alt = reschedule_booking(bs, bid, new_start, ks, GMIN, GMAX, now)
    reason = "-" if r is None else r.reason.value + (f"(id={r.conflict_booking_id})" if r.conflict_booking_id else "")
    return code, reason, alt

def _a4_7():
    bs, ks = world(); code, reason, alt = rs(bs, ks, D(18))
    return f"{code.value}|start={bs[0].start.strftime('%H:%M')}"

def _a4_8():
    bs, ks = world(); code, reason, alt = rs(bs, ks, D(16))
    return f"{code.value}|start={bs[0].start.strftime('%H:%M')}|recheck18:00={chk(D(18), 60, 4, bs, ks)}"

def _a4_9():
    bs, ks = world(); code, reason, alt = rs(bs, ks, D(18, 50))
    return f"{code.value}|start={bs[0].start.strftime('%H:%M')}"

def _a4_10():
    bs, ks = world(); code, reason, alt = rs(bs, ks, D(19, 30))
    return f"{code.value}|{reason}|alt={hhmm(alt)}|start={bs[0].start.strftime('%H:%M')}"

def _a4_11():
    bs, ks = world(); code, reason, alt = rs(bs, ks, D(11))
    return f"{code.value}|{reason}|alt={hhmm(alt)}|start={bs[0].start.strftime('%H:%M')}"

def _a4_12():
    bs, ks = world(); [setattr(k, "status", ES.FAULTY) for k in ks[:5]]
    code, reason, alt = rs(bs, ks, D(16))
    return f"{code.value}|{reason}|start={bs[0].start.strftime('%H:%M')}"

def _a4_13():
    bs, ks = world(); return rs(bs, ks, D(16), now=D(18))[0].value

def _a4_14():
    bs, ks = world(); bs[0].status = BookingStatus.CANCELLED
    return rs(bs, ks, D(16))[0].value

def _a4_15():
    bs, ks = world(); code = mark_no_show(bs, 1, D(18, 14), 15)
    return f"{code.value}|{bs[0].status.value}"

def _a4_16():
    bs, ks = world(); code = mark_no_show(bs, 1, D(18, 15), 15)
    return f"{code.value}|{bs[0].status.value}|recheck={chk(D(18), 60, 4, bs, ks)}"

def _a4_17():
    bs, ks = world(); bs[0].status = BookingStatus.CANCELLED
    return mark_no_show(bs, 1, D(18, 30), 15).value

A4_CASES = [
    Case("A4-1", "Отмена B1 в 12:00; слот освободился", "OK|1000.0|cancelled|recheck=OK", _a4_1),
    Case("A4-2", "Отмена ровно в момент начала", "TOO_LATE|confirmed", _a4_2),
    Case("A4-3", "Отмена уже отменённой брони", "INVALID_STATE", _a4_3),
    Case("A4-4", "Отмена брони, по которой создан сеанс", "INVALID_STATE", _a4_4),
    Case("A4-5", "Неизвестный идентификатор", "NOT_FOUND", _a4_5),
    Case("A4-6", "Отмена при пустом расписании", "NOT_FOUND", _a4_6),
    Case("A4-7", "Перенос B1 на собственное время 18:00", "OK|start=18:00", _a4_7),
    Case("A4-8", "Перенос B1 на 16:00; прежний слот свободен", "OK|start=16:00|recheck18:00=OK", _a4_8),
    Case("A4-9", "Перенос B1 на 18:50: касание начала B2", "OK|start=18:50", _a4_9),
    Case("A4-10", "Перенос B1 на 19:30: пересечение с B2, бронь не меняется",
         "SLOT_UNAVAILABLE|CONFLICT(id=2)|alt=21:00,21:15,21:30|start=18:00", _a4_10),
    Case("A4-11", "Перенос в прошлое (11:00)", "SLOT_UNAVAILABLE|IN_THE_PAST|alt=|start=18:00", _a4_11),
    Case("A4-12", "Перенос при нехватке комплектов", "SLOT_UNAVAILABLE|NOT_ENOUGH_KITS|start=18:00", _a4_12),
    Case("A4-13", "Перенос, когда время брони уже наступило", "TOO_LATE", _a4_13),
    Case("A4-14", "Перенос отменённой брони", "INVALID_STATE", _a4_14),
    Case("A4-15", "Неявка за минуту до конца ожидания (18:14)", "TOO_EARLY|confirmed", _a4_15),
    Case("A4-16", "Неявка в 18:15; слот освободился", "OK|no_show|recheck=OK", _a4_16),
    Case("A4-17", "Неявка у отменённой брони", "INVALID_STATE", _a4_17),
]


# ------------------------- Сквозные сценарии ---------------------------------
def _e2e_1() -> str:
    bs, ks, rows, log = [], kits(), [], []
    b, r, _ = create_booking(101, 1, 3, D(18), 60, 4, 1000.0, GMIN, GMAX, bs, ks, NOW)
    s = Session(1, 4, 60); b.session_id = 1
    issue_equipment(s, ks, rows, D(17, 55), log)
    start_session(s, D(18, 2))
    replace_equipment(s, 2, ks, rows, D(18, 20), log)
    code, rep = finish_session(s, bs, D(19, 5))
    return_equipment(s, rows, ks, D(19, 6), {1: "ok", 3: "ok", 4: "ok", 5: "ok"}, log)
    for k in ks:
        if k.status == ES.RETURNED_PENDING:
            change_status(k, ES.SERVICING, D(19, 20), "дезинфекция, зарядка", log)
            change_status(k, ES.AVAILABLE, D(19, 40), "готов", log)
    nxt = check_slot_availability(D(19, 15), 30, 4, GMIN, GMAX, bs, ks, D(19, 6), 10)
    return (f"booking={b.status.value}|session={s.status.value}|actual={rep.actual_min}"
            f"|over={rep.overtime_min}|kits1-5={','.join(k.status.value for k in ks[:5])}"
            f"|log={len(log)}|rows_open={sum(x.returned_at is None for x in rows)}"
            f"|next_slot={nxt.reason.value}")

def _e2e_2() -> str:
    bs, ks = [], kits()
    b1_, r1, _ = create_booking(101, 1, 3, D(18), 60, 4, 0.0, GMIN, GMAX, bs, ks, NOW)
    b2_, r2, alt = create_booking(102, 1, 3, D(18), 60, 4, 0.0, GMIN, GMAX, bs, ks, NOW)
    code, _ = cancel_booking(bs, b1_.booking_id, D(13))
    b3_, r3, _ = create_booking(102, 1, 3, D(18), 60, 4, 0.0, GMIN, GMAX, bs, ks, D(13))
    return (f"{r1.reason.value}(id={b1_.booking_id})|{r2.reason.value}(id={r2.conflict_booking_id})"
            f"|alt={hhmm(alt)}|cancel={code.value}|retry={r3.reason.value}(id={b3_.booking_id})|n={len(bs)}")

E2E_CASES = [
    Case("E2E-1", "Полный цикл: бронь, выдача, старт, замена комплекта, завершение, возврат, обработка",
         "booking=completed|session=completed|actual=63|over=3"
         "|kits1-5=available,faulty,available,available,available|log=18|rows_open=0|next_slot=OK", _e2e_1),
    Case("E2E-2", "Конфликт слотов, отмена, повторная бронь",
         "OK(id=1)|CONFLICT(id=1)|alt=19:15,19:30,19:45|cancel=OK|retry=OK(id=2)|n=2", _e2e_2),
]

ALL_GROUPS = {"А1": A1_CASES, "А2": A2_CASES, "А3": A3_CASES, "А4": A4_CASES, "Сквозные": E2E_CASES}
