"""
Servicio de reserva de citas (booking).

Maneja la creación de citas con prevención de double-booking.
Sincroniza automáticamente con Google Calendar del doctor.
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.database.models import Appointment, Patient, Doctor, AppointmentType, AppointmentStatus
from src.services.availability_service import AvailabilityService
from src.calendar.service import CalendarService

logger = structlog.get_logger(__name__)


class BookingError(Exception):
    """Error durante el proceso de reserva."""
    pass


class SlotNotAvailableError(BookingError):
    """El slot solicitado no está disponible."""
    pass


class BookingService:
    """
    Servicio para reservar citas médicas.

    Implementa prevención de double-booking mediante transacciones.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.availability_service = AvailabilityService(session)
        self.calendar_service = CalendarService()

    async def book_appointment(
        self,
        patient_id: int,
        doctor_id: int,
        appointment_date: datetime,
        appointment_type_id: int,
        notes: Optional[str] = None
    ) -> Appointment:
        """
        Reserva una cita para un paciente.

        Args:
            patient_id: ID del paciente
            doctor_id: ID del doctor
            appointment_date: Fecha y hora de la cita
            appointment_type_id: Tipo de atención
            notes: Notas opcionales

        Returns:
            La cita creada

        Raises:
            BookingError: Si no se puede reservar
            SlotNotAvailableError: Si el slot no está disponible
        """
        # 1. Verificar que el paciente existe
        patient = await self._get_patient(patient_id)
        if not patient:
            raise BookingError(f"Paciente {patient_id} no encontrado")

        # 2. Verificar que el doctor existe
        doctor = await self._get_doctor(doctor_id)
        if not doctor:
            raise BookingError(f"Doctor {doctor_id} no encontrado")

        # 3. Verificar que el tipo de atención existe
        appointment_type = await self._get_appointment_type(appointment_type_id)
        if not appointment_type:
            raise BookingError(f"Tipo de atención {appointment_type_id} no encontrado")

        # 4. Verificar que el slot está disponible
        is_available = await self._check_slot_availability(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            duration_minutes=appointment_type.duration_minutes
        )

        if not is_available:
            raise SlotNotAvailableError(
                f"El slot {appointment_date.strftime('%Y-%m-%d %H:%M')} no está disponible"
            )

        # 5. Crear la cita
        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_type_id=appointment_type_id,
            appointment_date=appointment_date,
            doctor_name=f"{doctor.first_name} {doctor.last_name}",  # Mantener por compatibilidad
            specialty=doctor.specialty,
            status=AppointmentStatus.PENDING,
            notes=notes
        )

        self.session.add(appointment)
        await self.session.flush()  # Para obtener el ID antes de commit

        # 6. Sincronizar con Google Calendar del doctor
        if doctor.calendar_email:
            try:
                # Calcular end_time
                end_time = appointment_date + timedelta(minutes=appointment_type.duration_minutes)

                # Crear evento en calendar del doctor
                event_id = await self.calendar_service.create_event(
                    summary=f"Cita: {patient.first_name} {patient.last_name}",
                    start_time=appointment_date,
                    end_time=end_time,
                    description=f"Tipo: {appointment_type.name}\nPaciente: {patient.first_name} {patient.last_name}\nRUT: {patient.rut}\nTeléfono: {patient.phone}\n\nNotas: {notes or 'Sin notas'}",
                    status=appointment.status.value,
                    calendar_id=doctor.calendar_email
                )

                if event_id:
                    appointment.calendar_event_id = event_id
                    logger.info(
                        "appointment_synced_to_calendar",
                        appointment_id=appointment.id,
                        event_id=event_id,
                        doctor_email=doctor.calendar_email
                    )
                else:
                    logger.warning(
                        "failed_to_sync_appointment_to_calendar",
                        appointment_id=appointment.id,
                        doctor_email=doctor.calendar_email
                    )

            except Exception as e:
                # No fallar el booking si falla el calendario
                logger.error(
                    "error_syncing_appointment_to_calendar",
                    appointment_id=appointment.id,
                    error=str(e),
                    exc_info=True
                )

        return appointment

    async def cancel_appointment(
        self,
        appointment_id: int,
        cancel_reason: Optional[str] = None
    ) -> Appointment:
        """
        Cancela una cita existente.

        Args:
            appointment_id: ID de la cita
            cancel_reason: Razón de cancelación (se guarda en notes)

        Returns:
            La cita cancelada

        Raises:
            BookingError: Si la cita no existe o ya está cancelada
        """
        # Buscar la cita
        result = await self.session.execute(
            select(Appointment).where(Appointment.id == appointment_id)
        )
        appointment = result.scalar_one_or_none()

        if not appointment:
            raise BookingError(f"Cita {appointment_id} no encontrada")

        if appointment.status == AppointmentStatus.CANCELLED:
            raise BookingError(f"Cita {appointment_id} ya está cancelada")

        # Cancelar
        appointment.status = AppointmentStatus.CANCELLED
        if cancel_reason:
            appointment.notes = f"{appointment.notes or ''}\nCancelada: {cancel_reason}".strip()

        await self.session.flush()

        # Sincronizar con Google Calendar - eliminar evento
        if appointment.calendar_event_id and appointment.doctor:
            try:
                calendar_id = appointment.doctor.calendar_email or "primary"
                success = await self.calendar_service.delete_event(
                    event_id=appointment.calendar_event_id,
                    calendar_id=calendar_id
                )

                if success:
                    logger.info(
                        "appointment_deleted_from_calendar",
                        appointment_id=appointment.id,
                        event_id=appointment.calendar_event_id
                    )
                else:
                    logger.warning(
                        "failed_to_delete_appointment_from_calendar",
                        appointment_id=appointment.id,
                        event_id=appointment.calendar_event_id
                    )

            except Exception as e:
                logger.error(
                    "error_deleting_appointment_from_calendar",
                    appointment_id=appointment.id,
                    error=str(e),
                    exc_info=True
                )

        return appointment

    async def confirm_appointment(
        self,
        appointment_id: int
    ) -> Appointment:
        """
        Confirma una cita pendiente.

        Args:
            appointment_id: ID de la cita

        Returns:
            La cita confirmada

        Raises:
            BookingError: Si la cita no existe o no está pendiente
        """
        result = await self.session.execute(
            select(Appointment).where(Appointment.id == appointment_id)
        )
        appointment = result.scalar_one_or_none()

        if not appointment:
            raise BookingError(f"Cita {appointment_id} no encontrada")

        if appointment.status != AppointmentStatus.PENDING:
            raise BookingError(
                f"Cita {appointment_id} no está pendiente (estado actual: {appointment.status})"
            )

        appointment.status = AppointmentStatus.CONFIRMED
        await self.session.flush()

        # Sincronizar con Google Calendar - actualizar color
        if appointment.calendar_event_id and appointment.doctor:
            try:
                calendar_id = appointment.doctor.calendar_email or "primary"
                success = await self.calendar_service.update_event_color(
                    event_id=appointment.calendar_event_id,
                    status=appointment.status.value,
                    calendar_id=calendar_id
                )

                if success:
                    logger.info(
                        "appointment_color_updated_in_calendar",
                        appointment_id=appointment.id,
                        event_id=appointment.calendar_event_id,
                        status=appointment.status.value
                    )
                else:
                    logger.warning(
                        "failed_to_update_appointment_color_in_calendar",
                        appointment_id=appointment.id,
                        event_id=appointment.calendar_event_id
                    )

            except Exception as e:
                logger.error(
                    "error_updating_appointment_color_in_calendar",
                    appointment_id=appointment.id,
                    error=str(e),
                    exc_info=True
                )

        return appointment

    async def _get_patient(self, patient_id: int) -> Optional[Patient]:
        """Obtiene un paciente por ID."""
        result = await self.session.execute(
            select(Patient).where(Patient.id == patient_id)
        )
        return result.scalar_one_or_none()

    async def _get_doctor(self, doctor_id: int) -> Optional[Doctor]:
        """Obtiene un doctor por ID."""
        result = await self.session.execute(
            select(Doctor).where(
                and_(
                    Doctor.id == doctor_id,
                    Doctor.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()

    async def _get_appointment_type(self, appointment_type_id: int) -> Optional[AppointmentType]:
        """Obtiene un tipo de atención por ID."""
        result = await self.session.execute(
            select(AppointmentType).where(AppointmentType.id == appointment_type_id)
        )
        return result.scalar_one_or_none()

    async def _check_slot_availability(
        self,
        doctor_id: int,
        appointment_date: datetime,
        duration_minutes: int
    ) -> bool:
        """
        Verifica si un slot específico está disponible.

        Usa SELECT FOR UPDATE para prevenir race conditions.
        """
        appointment_end = appointment_date + timedelta(minutes=duration_minutes)

        # Buscar citas existentes que se solapen con este slot
        # Usa FOR UPDATE para lock de fila (prevenir double-booking)
        result = await self.session.execute(
            select(Appointment)
            .where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    Appointment.appointment_date < appointment_end,
                    Appointment.status.in_([
                        AppointmentStatus.PENDING,
                        AppointmentStatus.CONFIRMED
                    ])
                )
            )
            .with_for_update()  # Lock para prevenir race conditions
        )

        existing_appointments = result.scalars().all()

        # Verificar overlaps
        for existing in existing_appointments:
            # Calcular fin de la cita existente
            if existing.appointment_type:
                existing_end = existing.appointment_date + timedelta(
                    minutes=existing.appointment_type.duration_minutes
                )
            else:
                existing_end = existing.appointment_date + timedelta(minutes=20)  # Default

            # Verificar overlap
            # Hay overlap si: nuevo_start < existing_end AND nuevo_end > existing_start
            if appointment_date < existing_end and appointment_end > existing.appointment_date:
                return False  # Hay overlap - slot NO disponible

        return True  # No hay overlaps - slot disponible
