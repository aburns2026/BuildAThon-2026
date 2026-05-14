from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import desc
from sqlalchemy.orm import Session

try:
    from .models import AuditEvent, CompTimeAdjustment, Employee, LeaveRequest, ScheduledShift, Shift, TimeCorrection
except ImportError:
    from models import AuditEvent, CompTimeAdjustment, Employee, LeaveRequest, ScheduledShift, Shift, TimeCorrection


def utc_now() -> datetime:
    return datetime.now(UTC)


def utc_now_iso() -> str:
    return utc_now().isoformat()


def shift_to_dict(shift: Shift) -> dict:
    return {
        "shift_id": shift.shift_id,
        "employee_id": shift.employee_id,
        "start_at": shift.start_at.isoformat(),
        "end_at": shift.end_at.isoformat() if shift.end_at else None,
        "duration_minutes": shift.duration_minutes,
        "state": shift.state,
    }


def event_to_dict(event: AuditEvent) -> dict:
    return {
        "event_id": event.event_id,
        "employee_id": event.employee_id,
        "event_type": event.event_type,
        "event_at": event.event_at.isoformat(),
        "details": event.details,
    }


def leave_request_to_dict(item: LeaveRequest) -> dict:
    return {
        "leave_request_id": item.leave_request_id,
        "employee_id": item.employee_id,
        "start_date": item.start_date,
        "end_date": item.end_date,
        "status": item.status,
        "created_at": item.created_at.isoformat(),
        "approved_at": item.approved_at.isoformat() if item.approved_at else None,
    }


def scheduled_shift_to_dict(item: ScheduledShift) -> dict:
    return {
        "scheduled_shift_id": item.scheduled_shift_id,
        "employee_id": item.employee_id,
        "start_at": item.start_at.isoformat(),
        "end_at": item.end_at.isoformat(),
        "break_minutes": item.break_minutes,
        "break_compliant": bool(item.break_compliant),
        "covers_core_hours": bool(item.covers_core_hours),
        "status": item.status,
    }


def time_correction_to_dict(item: TimeCorrection) -> dict:
    return {
        "correction_id": item.correction_id,
        "employee_id": item.employee_id,
        "reason": item.reason,
        "requested_at": item.requested_at.isoformat(),
        "status": item.status,
    }


def comp_time_adjustment_to_dict(item: CompTimeAdjustment) -> dict:
    return {
        "adjustment_id": item.adjustment_id,
        "employee_id": item.employee_id,
        "minutes_delta": item.minutes_delta,
        "reason": item.reason,
        "created_at": item.created_at.isoformat(),
    }


def add_audit_event(db: Session, employee_id: str, event_type: str, details: str) -> AuditEvent:
    event = AuditEvent(
        event_id=str(uuid4()),
        employee_id=employee_id,
        event_type=event_type,
        event_at=utc_now(),
        details=details,
    )
    db.add(event)
    return event


def ensure_seed_employee(db: Session) -> None:
    if db.get(Employee, "E001") is None:
        db.add(Employee(employee_id="E001", company_id="COMP-001", location_id="LOC-001"))
        db.commit()


def get_open_shift(db: Session, employee_id: str) -> Shift | None:
    return (
        db.query(Shift)
        .filter(Shift.employee_id == employee_id, Shift.state == "OPEN")
        .order_by(desc(Shift.start_at))
        .first()
    )


def list_closed_shifts(db: Session, employee_id: str) -> list[Shift]:
    return (
        db.query(Shift)
        .filter(Shift.employee_id == employee_id, Shift.state == "CLOSED")
        .order_by(Shift.start_at)
        .all()
    )


def compute_night_minutes(start_at: datetime, end_at: datetime | None) -> int:
    if end_at is None or end_at <= start_at:
        return 0
    cursor = start_at
    night_minutes = 0
    while cursor < end_at:
        if cursor.hour >= 22 or cursor.hour < 6:
            night_minutes += 1
        cursor += timedelta(minutes=1)
    return night_minutes


def is_holiday_shift(start_at: datetime) -> bool:
    return start_at.date().weekday() >= 5


def payroll_metrics(db: Session, employee_id: str) -> dict:
    closed = list_closed_shifts(db, employee_id)
    total_minutes = sum(int(shift.duration_minutes or 0) for shift in closed)
    overtime_minutes = sum(max(0, int(shift.duration_minutes or 0) - 480) for shift in closed)
    holiday_minutes = sum(int(shift.duration_minutes or 0) for shift in closed if is_holiday_shift(shift.start_at))
    night_shift_minutes = sum(compute_night_minutes(shift.start_at, shift.end_at) for shift in closed)
    return {
        "total_minutes": total_minutes,
        "overtime_minutes": overtime_minutes,
        "holiday_minutes": holiday_minutes,
        "night_shift_minutes": night_shift_minutes,
        "closed_shift_count": len(closed),
    }
