"""Persist corrections and balance adjustments

Revision ID: 0002_persist_adjustments_and_corrections
Revises: 0001_initial_schema
Create Date: 2026-05-14 00:00:01
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_persist_adjustments_and_corrections"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "time_corrections",
        sa.Column("correction_id", sa.String(length=64), nullable=False),
        sa.Column("employee_id", sa.String(length=32), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.employee_id"]),
        sa.PrimaryKeyConstraint("correction_id"),
    )
    op.create_index(op.f("ix_time_corrections_employee_id"), "time_corrections", ["employee_id"], unique=False)

    op.create_table(
        "pto_adjustments",
        sa.Column("adjustment_id", sa.String(length=64), nullable=False),
        sa.Column("employee_id", sa.String(length=32), nullable=False),
        sa.Column("days_delta", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.employee_id"]),
        sa.PrimaryKeyConstraint("adjustment_id"),
    )
    op.create_index(op.f("ix_pto_adjustments_employee_id"), "pto_adjustments", ["employee_id"], unique=False)

    op.create_table(
        "comp_time_adjustments",
        sa.Column("adjustment_id", sa.String(length=64), nullable=False),
        sa.Column("employee_id", sa.String(length=32), nullable=False),
        sa.Column("minutes_delta", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.employee_id"]),
        sa.PrimaryKeyConstraint("adjustment_id"),
    )
    op.create_index(
        op.f("ix_comp_time_adjustments_employee_id"),
        "comp_time_adjustments",
        ["employee_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_comp_time_adjustments_employee_id"), table_name="comp_time_adjustments")
    op.drop_table("comp_time_adjustments")

    op.drop_index(op.f("ix_pto_adjustments_employee_id"), table_name="pto_adjustments")
    op.drop_table("pto_adjustments")

    op.drop_index(op.f("ix_time_corrections_employee_id"), table_name="time_corrections")
    op.drop_table("time_corrections")