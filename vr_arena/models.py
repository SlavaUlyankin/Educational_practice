"""Модели данных и параметры (соответствуют ER-диаграмме, рис. 9, и таблице 11)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import NamedTuple, Optional

# --- Параметры точки (таблица 11; значения предполагаемые, не из источников) ---
PREP_MIN: int = 10          # интервал на подготовку между сеансами, мин
WARN_MIN: int = 5           # порог «сеанс подходит к концу», мин
NO_SHOW_WAIT_MIN: int = 15  # срок ожидания группы до фиксации неявки, мин
STEP_MIN: int = 15          # шаг поиска альтернативных слотов, мин
HORIZON_H: int = 4          # горизонт поиска альтернатив, часов
MAX_ALTERNATIVES: int = 3   # максимум предлагаемых альтернатив


class BookingStatus(str, Enum):
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class SessionStatus(str, Enum):
    PREPARED = "prepared"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class EquipmentStatus(str, Enum):
    AVAILABLE = "available"
    ISSUED = "issued"
    RETURNED_PENDING = "returned_pending"
    SERVICING = "servicing"
    FAULTY = "faulty"


class EquipmentKind(str, Enum):
    HEADSET = "headset_controllers"
    BACKPACK = "backpack_set"


class Reason(str, Enum):
    """Результат проверки слота (алгоритм А1.1)."""
    OK = "OK"
    INVALID_INPUT = "INVALID_INPUT"
    PLAYERS_OUT_OF_RANGE = "PLAYERS_OUT_OF_RANGE"
    IN_THE_PAST = "IN_THE_PAST"
    NOT_ENOUGH_KITS = "NOT_ENOUGH_KITS"
    CONFLICT = "CONFLICT"


class Code(str, Enum):
    """Коды результата операций А2, А3, А4."""
    OK = "OK"
    NOT_FOUND = "NOT_FOUND"
    INVALID_STATE = "INVALID_STATE"
    INVALID_INPUT = "INVALID_INPUT"
    INVALID_DURATION = "INVALID_DURATION"
    INVALID_TIME = "INVALID_TIME"
    TOO_LATE = "TOO_LATE"
    TOO_EARLY = "TOO_EARLY"
    SLOT_UNAVAILABLE = "SLOT_UNAVAILABLE"
    UNKNOWN_STATUS = "UNKNOWN_STATUS"
    INVALID_TRANSITION = "INVALID_TRANSITION"
    NOT_ENOUGH_AVAILABLE = "NOT_ENOUGH_AVAILABLE"
    ALREADY_ISSUED = "ALREADY_ISSUED"
    NO_ACTIVE_ISSUE = "NO_ACTIVE_ISSUE"
    MISSING_CONDITION = "MISSING_CONDITION"
    INCONSISTENT_STATE = "INCONSISTENT_STATE"
    NO_REPLACEMENT = "NO_REPLACEMENT"
    NOT_ISSUED = "NOT_ISSUED"


class TimeState(str, Enum):
    """Состояние сеанса по времени (алгоритм А2.2)."""
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    ENDING_SOON = "ENDING_SOON"
    TIME_UP = "TIME_UP"
    COMPLETED = "COMPLETED"
    INVALID_TIME = "INVALID_TIME"


@dataclass
class Booking:
    """Бронирование. duration_min берётся из тарифа при создании (в ER хранится в тарифе)."""
    booking_id: int
    client_id: int
    game_id: int
    tariff_id: int
    start: datetime
    duration_min: int
    players: int
    prepaid_amount: float = 0.0
    status: BookingStatus = BookingStatus.CONFIRMED
    session_id: Optional[int] = None


@dataclass
class Session:
    """Сеанс. duration_min — плановая длительность по тарифу."""
    session_id: int
    players_count: int
    duration_min: int
    status: SessionStatus = SessionStatus.PREPARED
    started_at: Optional[datetime] = None
    actual_end_at: Optional[datetime] = None


@dataclass
class EquipmentSet:
    equipment_id: int
    inventory_code: str
    kind: EquipmentKind = EquipmentKind.HEADSET
    status: EquipmentStatus = EquipmentStatus.AVAILABLE


@dataclass
class SessionEquipment:
    """Выдача комплекта в сеанс (связующая таблица)."""
    session_id: int
    equipment_id: int
    issued_at: datetime
    returned_at: Optional[datetime] = None
    return_condition: Optional[str] = None  # "ok" или "damaged"


@dataclass
class StatusLogEntry:
    equipment_id: int
    old_status: Optional[EquipmentStatus]
    new_status: EquipmentStatus
    changed_at: datetime
    comment: Optional[str] = None


@dataclass
class SlotCheckResult:
    available: bool
    reason: Reason
    conflict_booking_id: Optional[int] = None


class TimeStateResult(NamedTuple):
    state: TimeState
    remaining_min: int
    overtime_min: int


@dataclass
class FinishReport:
    planned_end: datetime
    actual_end: datetime
    actual_min: int
    overtime_min: int
