from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

try:
    from .db import Base
except ImportError:
    from db import Base


class Employee(Base):
    __tablename__ = "employees"

    employee_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(64), nullable=False)
    location_id: Mapped[str] = mapped_column(String(64), nullable=False)


class Shift(Base):
    __tablename__ = "shifts"

    shift_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees.employee_id"), nullable=False, index=True)
    start_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    state: Mapped[str] = mapped_column(String(16), nullable=False, index=True)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    event_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees.employee_id"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    event_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=False)


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    leave_request_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees.employee_id"), nullable=False, index=True)
    start_date: Mapped[str] = mapped_column(String(10), nullable=False)
    end_date: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    approved_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ScheduledShift(Base):
    __tablename__ = "scheduled_shifts"

    scheduled_shift_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees.employee_id"), nullable=False, index=True)
    start_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    break_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    break_compliant: Mapped[int] = mapped_column(Integer, nullable=False)
    covers_core_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)


class TimeCorrection(Base):
    __tablename__ = "time_corrections"

    correction_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees.employee_id"), nullable=False, index=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    requested_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)


class PtoAdjustment(Base):
    __tablename__ = "pto_adjustments"

    adjustment_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees.employee_id"), nullable=False, index=True)
    days_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)


class CompTimeAdjustment(Base):
    __tablename__ = "comp_time_adjustments"

    adjustment_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees.employee_id"), nullable=False, index=True)
    minutes_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)


class PolicySetting(Base):
    __tablename__ = "policy_settings"

    policy_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    int_value: Mapped[int] = mapped_column(Integer, nullable=False)


class NotificationEndpoint(Base):
    __tablename__ = "notification_endpoints"

    company_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    destination_type: Mapped[str] = mapped_column(String(32), nullable=False)
    target: Mapped[str] = mapped_column(String(255), nullable=False)
    secret_reference: Mapped[str | None] = mapped_column(String(128), nullable=True)
    enabled: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    last_tested_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SecretProviderConfig(Base):
    __tablename__ = "secret_provider_configs"

    company_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    reference_name: Mapped[str] = mapped_column(String(128), nullable=False)
    enabled: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
