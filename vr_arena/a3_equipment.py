"""Алгоритм А3 — статусы комплектов оборудования (рис. 12–13, таблицы 18–21)."""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Union

from .models import (
    Code, EquipmentKind, EquipmentSet, EquipmentStatus, Session,
    SessionEquipment, SessionStatus, StatusLogEntry,
)

S = EquipmentStatus
# Допустимые переходы статуса комплекта (таблица 9.1)
ALLOWED_TRANSITIONS: frozenset[tuple[EquipmentStatus, EquipmentStatus]] = frozenset({
    (S.AVAILABLE, S.ISSUED), (S.AVAILABLE, S.FAULTY),
    (S.ISSUED, S.RETURNED_PENDING), (S.ISSUED, S.FAULTY),
    (S.RETURNED_PENDING, S.SERVICING), (S.RETURNED_PENDING, S.FAULTY),
    (S.SERVICING, S.AVAILABLE), (S.SERVICING, S.FAULTY),
    (S.FAULTY, S.SERVICING),
})


def change_status(kit: EquipmentSet, new_status: Union[EquipmentStatus, str],
                  now: datetime, comment: Optional[str],
                  log: list[StatusLogEntry]) -> tuple[Code, EquipmentStatus]:
    """А3.1. Единственная функция, меняющая статус: проверка перехода + запись в журнал."""
    try:                                                    # D1
        target = EquipmentStatus(new_status)
    except ValueError:
        return Code.UNKNOWN_STATUS, kit.status
    old = kit.status                                        # P1
    if (old, target) not in ALLOWED_TRANSITIONS:            # D2 (в т.ч. old == target)
        return Code.INVALID_TRANSITION, old
    kit.status = target                                     # P2
    log.append(StatusLogEntry(kit.equipment_id, old, target, now, comment))  # P3
    return Code.OK, old


def select_available(kits: list[EquipmentSet], players: int,
                     kind: Optional[EquipmentKind] = None
                     ) -> tuple[Code, list[EquipmentSet], int]:
    """А3.2. Подбор доступных комплектов (только статус available)."""
    if players < 1:
        return Code.INVALID_INPUT, [], 0
    selected: list[EquipmentSet] = []
    for kit in kits:
        if kit.status == EquipmentStatus.AVAILABLE and (kind is None or kit.kind == kind):
            selected.append(kit)
            if len(selected) == players:
                break
    shortage = players - len(selected)
    if shortage == 0:
        return Code.OK, selected, 0
    return Code.NOT_ENOUGH_AVAILABLE, selected, shortage


def issue_equipment(session: Session, kits: list[EquipmentSet],
                    rows: list[SessionEquipment], now: datetime,
                    log: list[StatusLogEntry],
                    kind: Optional[EquipmentKind] = None
                    ) -> tuple[Code, list[int], int]:
    """А3.3. Выдача комплектов в сеанс; при нехватке данные не изменяются."""
    if session.status != SessionStatus.PREPARED:
        return Code.INVALID_STATE, [], 0
    for r in rows:
        if r.session_id == session.session_id and r.returned_at is None:
            return Code.ALREADY_ISSUED, [], 0
    code, selected, shortage = select_available(kits, session.players_count, kind)
    if code != Code.OK:
        return code, [], shortage
    for kit in selected:
        change_status(kit, EquipmentStatus.ISSUED, now, "выдан в сеанс", log)
        rows.append(SessionEquipment(session.session_id, kit.equipment_id, now))
    return Code.OK, [k.equipment_id for k in selected], 0


def return_equipment(session: Session, rows: list[SessionEquipment],
                     kits: list[EquipmentSet], now: datetime,
                     conditions: dict[int, str], log: list[StatusLogEntry]
                     ) -> tuple[Code, list[int]]:
    """А3.4. Возврат после сеанса: сначала проверка всех строк, затем применение."""
    if session.status != SessionStatus.COMPLETED:
        return Code.INVALID_STATE, []
    active = [r for r in rows
              if r.session_id == session.session_id and r.returned_at is None]
    if not active:
        return Code.NO_ACTIVE_ISSUE, []
    kit_by_id = {k.equipment_id: k for k in kits}
    for r in active:                                        # цикл 1: проверка
        cond = conditions.get(r.equipment_id)
        if cond not in ("ok", "damaged"):
            return Code.MISSING_CONDITION, []
        kit = kit_by_id.get(r.equipment_id)
        if (kit is None
                or kit.status not in (EquipmentStatus.ISSUED, EquipmentStatus.FAULTY)
                or (kit.status == EquipmentStatus.FAULTY and cond == "ok")):
            return Code.INCONSISTENT_STATE, []
    for r in active:                                        # цикл 2: применение
        cond = conditions[r.equipment_id]
        kit = kit_by_id[r.equipment_id]
        r.returned_at = now
        r.return_condition = cond
        target = (EquipmentStatus.FAULTY if cond == "damaged"
                  else EquipmentStatus.RETURNED_PENDING)
        if kit.status != target:
            change_status(kit, target, now, "возврат из сеанса", log)
    return Code.OK, [r.equipment_id for r in active]


def replace_equipment(session: Session, faulty_id: int, kits: list[EquipmentSet],
                      rows: list[SessionEquipment], now: datetime,
                      log: list[StatusLogEntry]
                      ) -> tuple[Code, Optional[int]]:
    """А3.5. Замена неисправного комплекта во время сеанса."""
    if session.status != SessionStatus.IN_PROGRESS:
        return Code.INVALID_STATE, None
    row = next((r for r in rows if r.session_id == session.session_id
                and r.equipment_id == faulty_id and r.returned_at is None), None)
    if row is None:
        return Code.NOT_ISSUED, None
    kit = next((k for k in kits if k.equipment_id == faulty_id), None)
    if kit is None or kit.status not in (EquipmentStatus.ISSUED, EquipmentStatus.FAULTY):
        return Code.INCONSISTENT_STATE, None
    if kit.status == EquipmentStatus.ISSUED:
        change_status(kit, EquipmentStatus.FAULTY, now,
                      "неисправность во время сеанса", log)
    row.returned_at = now
    row.return_condition = "damaged"
    code, selected, _ = select_available(kits, 1, kit.kind)
    if code != Code.OK:
        return Code.NO_REPLACEMENT, None
    new = selected[0]
    change_status(new, EquipmentStatus.ISSUED, now, "замена комплекта", log)
    rows.append(SessionEquipment(session.session_id, new.equipment_id, now))
    return Code.OK, new.equipment_id
