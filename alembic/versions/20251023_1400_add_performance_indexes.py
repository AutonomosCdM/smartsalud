"""Add performance indexes for scalability

Revision ID: 20251023_1400
Revises: 20251023_1340
Create Date: 2025-10-23 14:00:00.000000

"""
from typing import Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251023_1400'
down_revision: Union[str, None] = '20251023_1340'
branch_labels: Union[str, tuple[str, ...], None] = None
depends_on: Union[str, tuple[str, ...], None] = None


def upgrade() -> None:
    # 1. Índice en appointments.doctor_id (CRÍTICO - query principal)
    op.create_index(
        'ix_appointments_doctor_id',
        'appointments',
        ['doctor_id']
    )

    # 2. Índice en appointments.appointment_type_id
    op.create_index(
        'ix_appointments_appointment_type_id',
        'appointments',
        ['appointment_type_id']
    )

    # 3. Índice en doctor_schedules.appointment_type_id
    op.create_index(
        'ix_doctor_schedules_appointment_type_id',
        'doctor_schedules',
        ['appointment_type_id']
    )

    # 4. Índice compuesto CRÍTICO para overlap detection
    # Este índice optimiza la query: WHERE doctor_id = X AND appointment_date < Y AND status IN (...)
    op.create_index(
        'ix_appointments_overlap_check',
        'appointments',
        ['doctor_id', 'appointment_date', 'status'],
        postgresql_where=sa.text("status IN ('PENDING', 'CONFIRMED')")  # Partial index
    )

    # 5. Índice para búsquedas por paciente + fecha
    op.create_index(
        'ix_appointments_patient_date',
        'appointments',
        ['patient_id', 'appointment_date']
    )


def downgrade() -> None:
    op.drop_index('ix_appointments_patient_date', table_name='appointments')
    op.drop_index('ix_appointments_overlap_check', table_name='appointments')
    op.drop_index('ix_doctor_schedules_appointment_type_id', table_name='doctor_schedules')
    op.drop_index('ix_appointments_appointment_type_id', table_name='appointments')
    op.drop_index('ix_appointments_doctor_id', table_name='appointments')
