"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-10-23 10:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial schema."""

    # Create patients table
    op.create_table(
        'patients',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('rut', sa.String(length=12), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rut'),
        sa.UniqueConstraint('phone')
    )
    op.create_index('ix_patients_rut', 'patients', ['rut'])
    op.create_index('ix_patients_phone', 'patients', ['phone'])

    # Create appointments table
    op.create_table(
        'appointments',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('appointment_date', sa.DateTime(), nullable=False),
        sa.Column('doctor_name', sa.String(length=200), nullable=False),
        sa.Column('specialty', sa.String(length=100), nullable=True),
        sa.Column(
            'status',
            sa.Enum('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED', 'NO_SHOW', name='appointmentstatus'),
            nullable=False,
            server_default='PENDING'
        ),
        sa.Column('calendar_event_id', sa.String(length=255), nullable=True, comment='Google Calendar event ID'),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('calendar_event_id')
    )
    op.create_index('ix_appointments_patient_id', 'appointments', ['patient_id'])
    op.create_index('ix_appointments_appointment_date', 'appointments', ['appointment_date'])
    op.create_index('ix_appointments_status', 'appointments', ['status'])
    op.create_index('ix_appointments_date_status', 'appointments', ['appointment_date', 'status'])

    # Create interactions table
    op.create_table(
        'interactions',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('appointment_id', sa.Integer(), nullable=True),
        sa.Column('message_from', sa.String(length=20), nullable=False),
        sa.Column('message_to', sa.String(length=20), nullable=False),
        sa.Column('message_body', sa.Text(), nullable=False),
        sa.Column('detected_intent', sa.String(length=50), nullable=True, comment='NLP detected intent (CONFIRM/CANCEL/UNKNOWN)'),
        sa.Column('confidence_score', sa.Integer(), nullable=True, comment='NLP confidence score 0-100'),
        sa.Column('twilio_message_sid', sa.String(length=100), nullable=True, comment='Twilio Message SID for deduplication'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('twilio_message_sid')
    )
    op.create_index('ix_interactions_patient_id', 'interactions', ['patient_id'])
    op.create_index('ix_interactions_appointment_id', 'interactions', ['appointment_id'])
    op.create_index('ix_interactions_created_at', 'interactions', ['created_at'])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('interactions')
    op.drop_table('appointments')
    op.drop_table('patients')

    # Drop enum type
    op.execute('DROP TYPE appointmentstatus')
