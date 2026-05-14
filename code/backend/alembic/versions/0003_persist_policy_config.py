"""Persist policy configuration

Revision ID: 0003_persist_policy_config
Revises: 0002_persist_adjustments_and_corrections
Create Date: 2026-05-14 00:00:02
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_persist_policy_config"
down_revision = "0002_persist_adjustments_and_corrections"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "policy_settings",
        sa.Column("policy_key", sa.String(length=64), nullable=False),
        sa.Column("int_value", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("policy_key"),
    )
    op.bulk_insert(
        sa.table(
            "policy_settings",
            sa.column("policy_key", sa.String(length=64)),
            sa.column("int_value", sa.Integer()),
        ),
        [
            {"policy_key": "minimum_break_minutes", "int_value": 30},
            {"policy_key": "core_hour_start", "int_value": 10},
            {"policy_key": "core_hour_end", "int_value": 15},
        ],
    )


def downgrade() -> None:
    op.drop_table("policy_settings")