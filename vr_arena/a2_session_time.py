"""Алгоритм А2 — контроль длительности сеанса (рис. 11, таблицы 15–17)."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from .models import (
    WARN_MIN, Booking, BookingStatus, Code, FinishReport, Session,
    SessionStatus, TimeState, TimeStateResult,
)


def start_session(session: Session, now: datetime) -> tuple[Code, Optional[datetime]]:
    """А2.1. Фиксирует время начала; возвращает плановое окончание."""
    if session.duration_min <= 0:
        return Code.INVALID_DURATION, None
    if session.status != SessionStatus.PREPARED:
        return Code.INVALID_STATE, None
    session.started_at = now
    session.status = SessionStatus.IN_PROGRESS
    return Code.OK, now + timedelta(minutes=session.duration_min)


def session_time_state(session: Session, now: datetime,
                       warn_min: int = WARN_MIN) -> TimeStateResult:
    """А2.2. Состояние сеанса по времени (чистая функция)."""
    if session.status == SessionStatus.PREPARED:                       # D1
        return TimeStateResult(TimeState.NOT_STARTED, 0, 0)
    if session.status == SessionStatus.COMPLETED:                      # D2
        return TimeStateResult(TimeState.COMPLETED, 0, 0)
    if session.started_at is None or now < session.started_at:         # D3
        return TimeStateResult(TimeState.INVALID_TIME, 0, 0)
    planned_end = session.started_at + timedelta(minutes=session.duration_min)  # P1
    remaining = (planned_end - now).total_seconds()
    if remaining > warn_min * 60:                                      # D4
        return TimeStateResult(TimeState.RUNNING, int(remaining // 60), 0)
    if remaining > 0:                                                  # D5
        return TimeStateResult(TimeState.ENDING_SOON, int(remaining // 60), 0)
    return TimeStateResult(TimeState.TIME_UP, 0, int((-remaining) // 60))  # P2


def finish_session(session: Session, bookings: list[Booking],
                   now: datetime) -> tuple[Code, Optional[FinishReport]]:
    """А2.3. Фиксирует окончание, считает фактическую длительность и превышение."""
    if session.status != SessionStatus.IN_PROGRESS:
        return Code.INVALID_STATE, None
    # started_at is None — защитная проверка: по ER у сеанса в работе время начала задано
    if session.started_at is None or now <= session.started_at:
        return Code.INVALID_TIME, None
    session.actual_end_at = now
    session.status = SessionStatus.COMPLETED
    planned_end = session.started_at + timedelta(minutes=session.duration_min)
    actual_min = int((now - session.started_at).total_seconds() // 60)
    overtime = max(0, int((now - planned_end).total_seconds() // 60))
    for b in bookings:
        if b.session_id == session.session_id and b.status == BookingStatus.CONFIRMED:
            b.status = BookingStatus.COMPLETED
    return Code.OK, FinishReport(planned_end, now, actual_min, overtime)


def sessions_needing_attention(sessions: list[Session], now: datetime,
                               warn_min: int = WARN_MIN
                               ) -> list[tuple[int, TimeStateResult]]:
    """А2.4. Сеансы в состояниях ENDING_SOON и TIME_UP."""
    result: list[tuple[int, TimeStateResult]] = []
    for s in sessions:
        if s.status != SessionStatus.IN_PROGRESS:
            continue
        st = session_time_state(s, now, warn_min)
        if st.state in (TimeState.ENDING_SOON, TimeState.TIME_UP):
            result.append((s.session_id, st))
    return result
