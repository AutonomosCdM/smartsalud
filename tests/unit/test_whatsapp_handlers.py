"""
Unit tests for WhatsApp handlers.
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from src.whatsapp.handlers import handle_confirm, handle_cancel, handle_unknown
from src.database.models import Patient, Appointment, AppointmentStatus
from src.database.repositories import PatientRepository, AppointmentRepository

pytestmark = pytest.mark.asyncio


class TestHandleConfirm:
    """Tests for confirm intent handler."""

    async def test_confirm_success(self, db_session: AsyncSession):
        """Test successful appointment confirmation."""
        # Create test patient
        patient_repo = PatientRepository(db_session)
        patient = await patient_repo.create(
            rut="11111111-1",
            phone="whatsapp:+56911111111",
            first_name="María",
            last_name="González"
        )

        # Create test appointment
        appointment_repo = AppointmentRepository(db_session)
        appointment = await appointment_repo.create(
            patient_id=patient.id,
            appointment_date=datetime.now() + timedelta(days=1),
            doctor_name="Dr. García",
            specialty="Medicina General"
        )
        await db_session.commit()

        # Handle confirm
        response = await handle_confirm(
            phone="whatsapp:+56911111111",
            message="Confirmo",
            db=db_session
        )

        # Verify response
        assert "CONFIRMADA" in response
        assert "María" in response
        assert "Dr. García" in response

        # Verify appointment status changed
        await db_session.refresh(appointment)
        assert appointment.status == AppointmentStatus.CONFIRMED

    async def test_confirm_patient_not_found(self, db_session: AsyncSession):
        """Test confirm with non-existent patient."""
        response = await handle_confirm(
            phone="whatsapp:+56999999999",
            message="Confirmo",
            db=db_session
        )

        assert "no está registrado" in response

    async def test_confirm_no_pending_appointment(self, db_session: AsyncSession):
        """Test confirm when patient has no pending appointments."""
        # Create test patient without appointments
        patient_repo = PatientRepository(db_session)
        await patient_repo.create(
            rut="22222222-2",
            phone="whatsapp:+56922222222",
            first_name="Pedro",
            last_name="Ramírez"
        )
        await db_session.commit()

        response = await handle_confirm(
            phone="whatsapp:+56922222222",
            message="Confirmo",
            db=db_session
        )

        assert "No encontramos citas pendientes" in response


class TestHandleCancel:
    """Tests for cancel intent handler."""

    async def test_cancel_success(self, db_session: AsyncSession):
        """Test successful appointment cancellation."""
        # Create test patient
        patient_repo = PatientRepository(db_session)
        patient = await patient_repo.create(
            rut="33333333-3",
            phone="whatsapp:+56933333333",
            first_name="Ana",
            last_name="Silva"
        )

        # Create test appointment
        appointment_repo = AppointmentRepository(db_session)
        appointment = await appointment_repo.create(
            patient_id=patient.id,
            appointment_date=datetime.now() + timedelta(days=2),
            doctor_name="Dr. López",
            specialty="Pediatría"
        )
        await db_session.commit()

        # Handle cancel
        response = await handle_cancel(
            phone="whatsapp:+56933333333",
            message="Cancelo",
            db=db_session
        )

        # Verify response
        assert "CANCELADA" in response
        assert "Ana" in response
        assert "Dr. López" in response

        # Verify appointment status changed
        await db_session.refresh(appointment)
        assert appointment.status == AppointmentStatus.CANCELLED

    async def test_cancel_patient_not_found(self, db_session: AsyncSession):
        """Test cancel with non-existent patient."""
        response = await handle_cancel(
            phone="whatsapp:+56999999999",
            message="Cancelo",
            db=db_session
        )

        assert "no está registrado" in response

    async def test_cancel_no_pending_appointment(self, db_session: AsyncSession):
        """Test cancel when patient has no pending appointments."""
        # Create test patient without appointments
        patient_repo = PatientRepository(db_session)
        await patient_repo.create(
            rut="44444444-4",
            phone="whatsapp:+56944444444",
            first_name="Luis",
            last_name="Martínez"
        )
        await db_session.commit()

        response = await handle_cancel(
            phone="whatsapp:+56944444444",
            message="Cancelo",
            db=db_session
        )

        assert "No encontramos citas pendientes" in response


class TestHandleUnknown:
    """Tests for unknown intent handler."""

    async def test_unknown_with_existing_patient(self, db_session: AsyncSession):
        """Test unknown intent with existing patient."""
        # Create test patient
        patient_repo = PatientRepository(db_session)
        await patient_repo.create(
            rut="55555555-5",
            phone="whatsapp:+56955555555",
            first_name="Carmen",
            last_name="Torres"
        )
        await db_session.commit()

        response = await handle_unknown(
            phone="whatsapp:+56955555555",
            message="Hola, necesito ayuda",
            db=db_session
        )

        assert "No entendí tu mensaje" in response
        assert "Confirmo" in response
        assert "Cancelo" in response

    async def test_unknown_with_new_patient(self, db_session: AsyncSession):
        """Test unknown intent with non-existent patient."""
        response = await handle_unknown(
            phone="whatsapp:+56999999999",
            message="Mensaje aleatorio",
            db=db_session
        )

        # Should still return help message
        assert "No entendí tu mensaje" in response
