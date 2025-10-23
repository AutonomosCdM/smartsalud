"""increase_phone_field_size

Revision ID: 91ad6e677502
Revises: 001
Create Date: 2025-10-23 11:17:45.223503-03:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91ad6e677502'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Increase phone field size from VARCHAR(20) to VARCHAR(30)
    op.alter_column('patients', 'phone',
                    existing_type=sa.String(length=20),
                    type_=sa.String(length=30),
                    existing_nullable=False)

    op.alter_column('interactions', 'message_from',
                    existing_type=sa.String(length=20),
                    type_=sa.String(length=30),
                    existing_nullable=False)

    op.alter_column('interactions', 'message_to',
                    existing_type=sa.String(length=20),
                    type_=sa.String(length=30),
                    existing_nullable=False)


def downgrade() -> None:
    # Revert phone field size back to VARCHAR(20)
    op.alter_column('interactions', 'message_to',
                    existing_type=sa.String(length=30),
                    type_=sa.String(length=20),
                    existing_nullable=False)

    op.alter_column('interactions', 'message_from',
                    existing_type=sa.String(length=30),
                    type_=sa.String(length=20),
                    existing_nullable=False)

    op.alter_column('patients', 'phone',
                    existing_type=sa.String(length=30),
                    type_=sa.String(length=20),
                    existing_nullable=False)
