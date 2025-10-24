"""Create schedule system for real CESFAM workflow

Revision ID: 20251023_1340
Revises: 20251023_1117_91ad6e677502_increase_phone_field_size
Create Date: 2025-10-23 13:40:00

Based on real CESFAM schedule:
- Multiple doctors per sector
- Different appointment types with specific durations
- Daily schedules with time blocks
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '20251023_1340'
down_revision = '91ad6e677502'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create appointment_types table
    op.create_table(
        'appointment_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color', sa.String(20), nullable=True),  # Para diferenciar visualmente
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create doctors table
    op.create_table(
        'doctors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('sector', sa.String(50), nullable=True),  # "Sector 1 y 2"
        sa.Column('specialty', sa.String(100), nullable=True),
        sa.Column('calendar_email', sa.String(255), nullable=True),  # Para Google Calendar
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create doctor_schedules table
    # Horarios de trabajo del doctor por día de la semana
    op.create_table(
        'doctor_schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('day_of_week', sa.Integer(), nullable=False),  # 0=Monday, 6=Sunday
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('appointment_type_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['appointment_type_id'], ['appointment_types.id'], ondelete='CASCADE')
    )

    # Add indexes
    op.create_index('idx_doctor_schedules_doctor_day', 'doctor_schedules', ['doctor_id', 'day_of_week'])
    op.create_index('idx_doctors_active', 'doctors', ['is_active'])

    # Add doctor_id and appointment_type_id to appointments table
    op.add_column('appointments', sa.Column('doctor_id', sa.Integer(), nullable=True))
    op.add_column('appointments', sa.Column('appointment_type_id', sa.Integer(), nullable=True))

    op.create_foreign_key(
        'fk_appointments_doctor',
        'appointments', 'doctors',
        ['doctor_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_appointments_appointment_type',
        'appointments', 'appointment_types',
        ['appointment_type_id'], ['id'],
        ondelete='SET NULL'
    )

    # Insert real appointment types from CESFAM
    op.execute("""
        INSERT INTO appointment_types (name, duration_minutes, description, color) VALUES
        ('Cons. Morbilidad', 20, 'Consulta de morbilidad', 'blue'),
        ('Salud Mental', 40, 'Atención de salud mental', 'purple'),
        ('Control o crónico', 30, 'Control de pacientes crónicos', 'orange'),
        ('Pausa Saludable', 20, 'Pausa saludable', 'gray'),
        ('Recetas', 30, 'Emisión de recetas', 'red')
    """)


def downgrade() -> None:
    # Drop foreign keys from appointments
    op.drop_constraint('fk_appointments_appointment_type', 'appointments', type_='foreignkey')
    op.drop_constraint('fk_appointments_doctor', 'appointments', type_='foreignkey')
    op.drop_column('appointments', 'appointment_type_id')
    op.drop_column('appointments', 'doctor_id')

    # Drop indexes
    op.drop_index('idx_doctors_active', table_name='doctors')
    op.drop_index('idx_doctor_schedules_doctor_day', table_name='doctor_schedules')

    # Drop tables
    op.drop_table('doctor_schedules')
    op.drop_table('doctors')
    op.drop_table('appointment_types')
