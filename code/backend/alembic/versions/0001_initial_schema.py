"""Initial workforce schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-01-01 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "employees",
        sa.Column("employee_id", sa.String(length=32), nullable=False),
        sa.Column("company_id", sa.String(length=64), nullable=False),
        sa.Column("location_id", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("employee_id"),
    )

    op.create_table(
        "audit_events",
        sa.Column("event_id", sa.String(length=64), nullable=False),
        sa.Column("employee_id", sa.String(length=32), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("event_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("details", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.employee_id"]),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_index(op.f("ix_audit_events_employee_id"), "audit_events", ["employee_id"], unique=False)

    op.create_table(
        "leave_requests",
        sa.Column("leave_request_id", sa.String(length=64), nullable=False),
        sa.Column("employee_id", sa.String(length=32), nullable=False),
        sa.Column("start_date", sa.String(length=10), nullable=False),
        sa.Column("end_date", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.employee_id"]),
        sa.PrimaryKeyConstraint("leave_request_id"),
    )
    op.create_index(op.f("ix_leave_requests_employee_id"), "leave_requests", ["employee_id"], unique=False)

    op.create_table(
        "scheduled_shifts",
        sa.Column("scheduled_shift_id", sa.String(length=64), nullable=False),
        sa.Column("employee_id", sa.String(length=32), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("break_minutes", sa.Integer(), nullable=False),
        sa.Column("break_compliant", sa.Integer(), nullable=False),
        sa.Column("covers_core_hours", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.employee_id"]),
        sa.PrimaryKeyConstraint("scheduled_shift_id"),
    )
    op.create_index(op.f("ix_scheduled_shifts_employee_id"), "scheduled_shifts", ["employee_id"], unique=False)

    op.create_table(
        "shifts",
        sa.Column("shift_id", sa.String(length=64), nullable=False),
        sa.Column("employee_id", sa.String(length=32), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("state", sa.String(length=16), nullable=False),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.employee_id"]),
        sa.PrimaryKeyConstraint("shift_id"),
    )
    op.create_index(op.f("ix_shifts_employee_id"), "shifts", ["employee_id"], unique=False)
    op.create_index(op.f("ix_shifts_state"), "shifts", ["state"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_shifts_state"), table_name="shifts")
    op.drop_index(op.f("ix_shifts_employee_id"), table_name="shifts")
    op.drop_table("shifts")

    op.drop_index(op.f("ix_scheduled_shifts_employee_id"), table_name="scheduled_shifts")
    op.drop_table("scheduled_shifts")

    op.drop_index(op.f("ix_leave_requests_employee_id"), table_name="leave_requests")
    op.drop_table("leave_requests")

    op.drop_index(op.f("ix_audit_events_employee_id"), table_name="audit_events")
    op.drop_table("audit_events")

    op.drop_table("employees")
