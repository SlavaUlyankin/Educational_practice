"""Модели данных процедурного прототипа: десять сущностей ER-модели."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import NamedTuple, Optional

# Параметры точки по умолчанию; у конкретной арены prep_min может отличаться.
PREP_MIN: int = 10
WARN_MIN: int = 5
NO_SHOW_WAIT_MIN: int = 15
STEP_MIN: int = 15
HORIZON_H: int = 4
MAX_ALTERNATIVES: int = 3


class BookingStatus(str, Enum):
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class BookingEventType(str, Enum):
    CREATED = "created"
    RESCHEDULED = "rescheduled"
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
    """Результат проверки слота (алгоритм А1)."""
    OK = "OK"
    INVALID_INPUT = "INVALID_INPUT"
    PLAYERS_OUT_OF_RANGE = "PLAYERS_OUT_OF_RANGE"
    IN_THE_PAST = "IN_THE_PAST"
    NOT_ENOUGH_KITS = "NOT_ENOUGH_KITS"
    CONFLICT = "CONFLICT"


class Code(str, Enum):
    """Коды результата операций А2–А5."""
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
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    ENDING_SOON = "ENDING_SOON"
    TIME_UP = "TIME_UP"
    COMPLETED = "COMPLETED"
    INVALID_TIME = "INVALID_TIME"


@dataclass
class Client:
    client_id: int
    full_name: str
    phone: str
    email: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class Game:
    game_id: int
    title: str
    min_players: int = 1
    max_players: int = 10
    allows_group_merge: bool = False


@dataclass
class Tariff:
    tariff_id: int
    name: str
    duration_min: int
    price_per_player: float
    prepayment_required: bool = False
    game_id: Optional[int] = None
    is_active: bool = True


@dataclass
class Arena:
    arena_id: int
    name: str
    capacity: int
    prep_min: int = PREP_MIN
    is_active: bool = True


@dataclass
class Booking:
    """Бронирование; duration_min — снимок длительности выбранного тарифа."""
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
    arena_id: int = 1
    created_at: Optional[datetime] = None
    history: list[BookingHistory] = field(default_factory=list, repr=False, compare=False)


@dataclass
class Session:
    session_id: int
    players_count: int
    duration_min: int
    status: SessionStatus = SessionStatus.PREPARED
    started_at: Optional[datetime] = None
    actual_end_at: Optional[datetime] = None
    arena_id: int = 1
    booking_id: Optional[int] = None


@dataclass
class EquipmentSet:
    equipment_id: int
    inventory_code: str
    kind: EquipmentKind = EquipmentKind.HEADSET
    status: EquipmentStatus = EquipmentStatus.AVAILABLE
    arena_id: int = 1

    def is_available_for_issue(self) -> bool:
        """Текущее состояние, без прогноза подготовки к будущему сеансу."""
        return self.status == EquipmentStatus.AVAILABLE


@dataclass
class SessionEquipment:
    session_id: int
    equipment_id: int
    issued_at: datetime
    returned_at: Optional[datetime] = None
    return_condition: Optional[str] = None


@dataclass
class StatusLogEntry:
    """Запись сущности equipment_status_log."""
    equipment_id: int
    old_status: Optional[EquipmentStatus]
    new_status: EquipmentStatus
    changed_at: datetime
    comment: Optional[str] = None
    log_id: Optional[int] = None


# Название, совпадающее с сущностью ER; прежнее имя сохранено для совместимости.
EquipmentStatusLog = StatusLogEntry


@dataclass
class BookingHistory:
    history_id: int
    booking_id: int
    event_type: BookingEventType
    changed_at: datetime
    old_start_time: Optional[datetime] = None
    new_start_time: Optional[datetime] = None
    old_arena_id: Optional[int] = None
    new_arena_id: Optional[int] = None
    reason: Optional[str] = None


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
