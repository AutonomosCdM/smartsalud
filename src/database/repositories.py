"""
Database repositories for data access layer.

Provides async methods for querying and updating database entities.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import Patient, Appointment, Interaction, AppointmentStatus
import structlog

logger = structlog.get_logger(__name__)


class PatientRepository:
    """Repository for Patient operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_phone(self, phone: str) -> Optional[Patient]:
        """
        Get patient by WhatsApp phone number.

        Args:
            phone: WhatsApp phone number (format: whatsapp:+56XXXXXXXXX)

        Returns:
            Patient if found, None otherwise
        """
        stmt = select(Patient).where(Patient.phone == phone)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_rut(self, rut: str) -> Optional[Patient]:
        """
        Get patient by RUT.

        Args:
            rut: Chilean RUT (format: XXXXXXXX-X)

        Returns:
            Patient if found, None otherwise
        """
        stmt = select(Patient).where(Patient.rut == rut)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        rut: str,
        phone: str,
        first_name: str,
        last_name: str,
        email: Optional[str] = None
    ) -> Patient:
        """
        Create a new patient.

        Args:
            rut: Chilean RUT
            phone: WhatsApp phone number
            first_name: Patient first name
            last_name: Patient last name
            email: Optional email address

        Returns:
            Created patient
        """
        patient = Patient(
            rut=rut,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        self.session.add(patient)
        await self.session.flush()
        logger.info("patient_created", patient_id=patient.id, rut=rut)
        return patient

    async def get_by_id(self, patient_id: int) -> Optional[Patient]:
        """Get patient by ID."""
        stmt = select(Patient).where(Patient.id == patient_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class AppointmentRepository:
    """Repository for Appointment operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, appointment_id: int) -> Optional[Appointment]:
        """
        Get appointment by ID with patient relationship loaded.

        Args:
            appointment_id: Appointment ID

        Returns:
            Appointment if found, None otherwise
        """
        stmt = (
            select(Appointment)
            .options(selectinload(Appointment.patient))
            .where(Appointment.id == appointment_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_pending_for_patient(self, patient_id: int) -> Optional[Appointment]:
        """
        Get the next pending appointment for a patient.

        Finds the nearest future appointment with PENDING status.

        Args:
            patient_id: Patient ID

        Returns:
            Nearest pending appointment if found, None otherwise
        """
        stmt = (
            select(Appointment)
            .where(
                and_(
                    Appointment.patient_id == patient_id,
                    Appointment.status == AppointmentStatus.PENDING,
                    Appointment.appointment_date > datetime.utcnow()
                )
            )
            .order_by(Appointment.appointment_date)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_pending_appointments(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Appointment]:
        """
        Get all pending appointments in a date range.

        Used for reminder scheduler.

        Args:
            start_date: Start of date range
            end_date: End of date range

        Returns:
            List of pending appointments
        """
        stmt = (
            select(Appointment)
            .options(selectinload(Appointment.patient))
            .where(
                and_(
                    Appointment.status == AppointmentStatus.PENDING,
                    Appointment.appointment_date >= start_date,
                    Appointment.appointment_date < end_date
                )
            )
            .order_by(Appointment.appointment_date)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def confirm_appointment(self, appointment_id: int) -> bool:
        """
        Confirm an appointment.

        Args:
            appointment_id: Appointment ID

        Returns:
            True if confirmed, False if not found or already confirmed
        """
        appointment = await self.get_by_id(appointment_id)
        if not appointment:
            logger.warning("appointment_not_found", appointment_id=appointment_id)
            return False

        if appointment.status != AppointmentStatus.PENDING:
            logger.warning(
                "appointment_not_pending",
                appointment_id=appointment_id,
                current_status=appointment.status
            )
            return False

        appointment.status = AppointmentStatus.CONFIRMED
        appointment.updated_at = datetime.utcnow()
        await self.session.flush()

        logger.info(
            "appointment_confirmed",
            appointment_id=appointment_id,
            patient_id=appointment.patient_id
        )
        return True

    async def cancel_appointment(self, appointment_id: int) -> bool:
        """
        Cancel an appointment.

        Args:
            appointment_id: Appointment ID

        Returns:
            True if cancelled, False if not found or already cancelled
        """
        appointment = await self.get_by_id(appointment_id)
        if not appointment:
            logger.warning("appointment_not_found", appointment_id=appointment_id)
            return False

        if appointment.status in (AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED):
            logger.warning(
                "appointment_cannot_cancel",
                appointment_id=appointment_id,
                current_status=appointment.status
            )
            return False

        appointment.status = AppointmentStatus.CANCELLED
        appointment.updated_at = datetime.utcnow()
        await self.session.flush()

        logger.info(
            "appointment_cancelled",
            appointment_id=appointment_id,
            patient_id=appointment.patient_id
        )
        return True

    async def create(
        self,
        patient_id: int,
        appointment_date: datetime,
        doctor_name: str,
        specialty: Optional[str] = None,
        notes: Optional[str] = None,
        calendar_event_id: Optional[str] = None
    ) -> Appointment:
        """
        Create a new appointment.

        Args:
            patient_id: Patient ID
            appointment_date: Date and time of appointment
            doctor_name: Doctor's name
            specialty: Medical specialty
            notes: Additional notes
            calendar_event_id: Google Calendar event ID

        Returns:
            Created appointment
        """
        appointment = Appointment(
            patient_id=patient_id,
            appointment_date=appointment_date,
            doctor_name=doctor_name,
            specialty=specialty,
            notes=notes,
            calendar_event_id=calendar_event_id,
            status=AppointmentStatus.PENDING
        )
        self.session.add(appointment)
        await self.session.flush()
        logger.info("appointment_created", appointment_id=appointment.id, patient_id=patient_id)
        return appointment


class InteractionRepository:
    """Repository for Interaction operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        patient_id: int,
        message_from: str,
        message_to: str,
        message_body: str,
        detected_intent: Optional[str] = None,
        confidence_score: Optional[int] = None,
        appointment_id: Optional[int] = None,
        twilio_message_sid: Optional[str] = None
    ) -> Interaction:
        """
        Create a new interaction log entry.

        Args:
            patient_id: Patient ID
            message_from: Sender WhatsApp number
            message_to: Recipient WhatsApp number
            message_body: Message text
            detected_intent: NLP detected intent
            confidence_score: NLP confidence (0-100)
            appointment_id: Related appointment ID
            twilio_message_sid: Twilio Message SID

        Returns:
            Created interaction
        """
        interaction = Interaction(
            patient_id=patient_id,
            message_from=message_from,
            message_to=message_to,
            message_body=message_body,
            detected_intent=detected_intent,
            confidence_score=confidence_score,
            appointment_id=appointment_id,
            twilio_message_sid=twilio_message_sid
        )
        self.session.add(interaction)
        await self.session.flush()
        logger.info(
            "interaction_logged",
            interaction_id=interaction.id,
            patient_id=patient_id,
            intent=detected_intent
        )
        return interaction

    async def get_by_message_sid(self, message_sid: str) -> Optional[Interaction]:
        """
        Get interaction by Twilio Message SID.

        Used for deduplication.

        Args:
            message_sid: Twilio Message SID

        Returns:
            Interaction if found, None otherwise
        """
        stmt = select(Interaction).where(Interaction.twilio_message_sid == message_sid)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
