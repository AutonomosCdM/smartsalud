"""
Servicio de disponibilidad de citas.

Calcula slots disponibles = doctor_schedules - appointments reservados.
Basado en best practices de sistemas de scheduling reales.
"""
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import Doctor, DoctorSchedule, Appointment, AppointmentType, AppointmentStatus


@dataclass
class AvailableSlot:
    """Slot de tiempo disponible para agendar."""
    start_datetime: datetime
    end_datetime: datetime
    doctor_id: int
    doctor_name: str
    appointment_type_id: int
    appointment_type_name: str
    duration_minutes: int


class AvailabilityService:
    """
    Servicio para calcular disponibilidad de citas.

    Implementa el patrón: Disponibilidad = Horarios - Citas Reservadas
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_available_slots(
        self,
        doctor_id: int,
        start_date: date,
        end_date: date,
        appointment_type_id: Optional[int] = None
    ) -> List[AvailableSlot]:
        """
        Obtiene slots disponibles para un doctor en un rango de fechas.

        Args:
            doctor_id: ID del doctor
            start_date: Fecha inicio del rango
            end_date: Fecha fin del rango (inclusive)
            appointment_type_id: Filtrar por tipo de atención (opcional)

        Returns:
            Lista de slots disponibles ordenados por fecha
        """
        # 1. Obtener doctor info
        doctor = await self._get_doctor(doctor_id)
        if not doctor:
            return []

        # 2. Obtener horarios recurrentes del doctor
        schedules = await self._get_doctor_schedules(
            doctor_id,
            appointment_type_id
        )

        if not schedules:
            return []

        # 3. Generar slots concretos desde horarios recurrentes
        potential_slots = self._generate_concrete_slots(
            schedules,
            doctor,
            start_date,
            end_date
        )

        # 4. Obtener citas ya reservadas
        booked_appointments = await self._get_booked_appointments(
            doctor_id,
            start_date,
            end_date
        )

        # 5. Filtrar slots ocupados
        available_slots = self._filter_available_slots(
            potential_slots,
            booked_appointments
        )

        # 6. Ordenar por fecha
        available_slots.sort(key=lambda s: s.start_datetime)

        return available_slots

    async def _get_doctor(self, doctor_id: int) -> Optional[Doctor]:
        """Obtiene información del doctor."""
        result = await self.session.execute(
            select(Doctor).where(
                and_(
                    Doctor.id == doctor_id,
                    Doctor.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()

    async def _get_doctor_schedules(
        self,
        doctor_id: int,
        appointment_type_id: Optional[int] = None
    ) -> List[DoctorSchedule]:
        """
        Obtiene los horarios recurrentes del doctor.
        """
        query = select(DoctorSchedule).options(
            selectinload(DoctorSchedule.appointment_type)
        ).where(
            and_(
                DoctorSchedule.doctor_id == doctor_id,
                DoctorSchedule.is_active == True
            )
        )

        if appointment_type_id:
            query = query.where(
                DoctorSchedule.appointment_type_id == appointment_type_id
            )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    def _generate_concrete_slots(
        self,
        schedules: List[DoctorSchedule],
        doctor: Doctor,
        start_date: date,
        end_date: date
    ) -> List[AvailableSlot]:
        """
        Convierte horarios recurrentes en slots concretos con fechas específicas.

        Ejemplo:
        Input: Schedule(day_of_week=0, start=08:00, end=08:20)  # Lunes
        Output: [
            AvailableSlot(start=2025-10-27 08:00, end=2025-10-27 08:20),
            AvailableSlot(start=2025-11-03 08:00, end=2025-11-03 08:20),
            ...
        ]
        """
        slots = []
        current_date = start_date

        while current_date <= end_date:
            # día de la semana: 0=Lunes, 6=Domingo (como en DoctorSchedule)
            weekday = current_date.weekday()

            # Buscar schedules para este día de la semana
            for schedule in schedules:
                if schedule.day_of_week == weekday:
                    # Crear datetime combinando fecha + hora
                    start_dt = datetime.combine(current_date, schedule.start_time)
                    end_dt = datetime.combine(current_date, schedule.end_time)

                    # Crear slot disponible
                    slot = AvailableSlot(
                        start_datetime=start_dt,
                        end_datetime=end_dt,
                        doctor_id=doctor.id,
                        doctor_name=f"{doctor.first_name} {doctor.last_name}",
                        appointment_type_id=schedule.appointment_type_id,
                        appointment_type_name=schedule.appointment_type.name,
                        duration_minutes=schedule.appointment_type.duration_minutes
                    )
                    slots.append(slot)

            current_date += timedelta(days=1)

        return slots

    async def _get_booked_appointments(
        self,
        doctor_id: int,
        start_date: date,
        end_date: date
    ) -> List[Appointment]:
        """
        Obtiene citas ya reservadas para el doctor en el rango de fechas.

        Solo considera citas activas (PENDING, CONFIRMED).
        """
        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)

        result = await self.session.execute(
            select(Appointment).options(
                selectinload(Appointment.appointment_type)
            ).where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    Appointment.appointment_date >= start_datetime,
                    Appointment.appointment_date <= end_datetime,
                    Appointment.status.in_([
                        AppointmentStatus.PENDING,
                        AppointmentStatus.CONFIRMED
                    ])
                )
            )
        )
        return list(result.scalars().all())

    def _filter_available_slots(
        self,
        potential_slots: List[AvailableSlot],
        booked_appointments: List[Appointment]
    ) -> List[AvailableSlot]:
        """
        Filtra slots que están ocupados por citas existentes.

        Un slot está ocupado si hay overlap con una cita:
        - Slot: 08:00 - 08:20
        - Cita: 08:00 - 08:20 (mismo horario)
        - Resultado: Slot ocupado
        """
        available = []

        for slot in potential_slots:
            is_available = True

            for appointment in booked_appointments:
                # Calcular fin de la cita
                if appointment.appointment_type:
                    appointment_end = appointment.appointment_date + timedelta(
                        minutes=appointment.appointment_type.duration_minutes
                    )
                else:
                    # Default 20 min si no hay tipo
                    appointment_end = appointment.appointment_date + timedelta(minutes=20)

                # Verificar overlap
                # Hay overlap si: slot_start < appointment_end AND slot_end > appointment_start
                if (slot.start_datetime < appointment_end and
                    slot.end_datetime > appointment.appointment_date):
                    is_available = False
                    break

            if is_available:
                available.append(slot)

        return available

    async def get_next_available_slot(
        self,
        doctor_id: int,
        appointment_type_id: Optional[int] = None,
        days_ahead: int = 30
    ) -> Optional[AvailableSlot]:
        """
        Encuentra el próximo slot disponible para un doctor.

        Args:
            doctor_id: ID del doctor
            appointment_type_id: Tipo de atención (opcional)
            days_ahead: Días hacia adelante para buscar (default 30)

        Returns:
            Primer slot disponible o None si no hay
        """
        today = date.today()
        end_date = today + timedelta(days=days_ahead)

        slots = await self.get_available_slots(
            doctor_id=doctor_id,
            start_date=today,
            end_date=end_date,
            appointment_type_id=appointment_type_id
        )

        # Filtrar solo slots futuros (en caso de que haya slots en el pasado del día de hoy)
        now = datetime.now()
        future_slots = [s for s in slots if s.start_datetime > now]

        return future_slots[0] if future_slots else None
