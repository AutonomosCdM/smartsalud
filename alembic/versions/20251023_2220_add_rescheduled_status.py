"""add rescheduled status

Revision ID: 20251023_2220
Revises: 20251023_1400
Create Date: 2025-10-23 22:20:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251023_2220'
down_revision = '20251023_1400'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add RESCHEDULED to appointmentstatus enum
    op.execute("ALTER TYPE appointmentstatus ADD VALUE IF NOT EXISTS 'RESCHEDULED'")


def downgrade() -> None:
    # Cannot remove values from enum in PostgreSQL without recreating the type
    pass
