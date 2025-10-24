"""Stats API endpoints for dashboard."""
from datetime import datetime, date
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel

from src.database.connection import get_db
from src.database.models import Appointment, Patient, Doctor, AppointmentStatus

router = APIRouter()


class DashboardStats(BaseModel):
    """Dashboard statistics response."""
    total_appointments: int
    appointments_today: int
    pending_appointments: int
    confirmed_appointments: int
    rescheduled_appointments: int
    cancelled_appointments: int
    total_patients: int
    active_doctors: int


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    session: AsyncSession = Depends(get_db)
):
    """Get dashboard statistics."""

    # Total appointments
    total_appointments_query = select(func.count(Appointment.id))
    total_appointments_result = await session.execute(total_appointments_query)
    total_appointments = total_appointments_result.scalar() or 0

    # Appointments today
    today = date.today()
    appointments_today_query = select(func.count(Appointment.id)).where(
        func.date(Appointment.appointment_date) == today
    )
    appointments_today_result = await session.execute(appointments_today_query)
    appointments_today = appointments_today_result.scalar() or 0

    # Pending appointments
    pending_query = select(func.count(Appointment.id)).where(
        Appointment.status == AppointmentStatus.PENDING
    )
    pending_result = await session.execute(pending_query)
    pending_appointments = pending_result.scalar() or 0

    # Confirmed appointments
    confirmed_query = select(func.count(Appointment.id)).where(
        Appointment.status == AppointmentStatus.CONFIRMED
    )
    confirmed_result = await session.execute(confirmed_query)
    confirmed_appointments = confirmed_result.scalar() or 0

    # Rescheduled appointments
    rescheduled_query = select(func.count(Appointment.id)).where(
        Appointment.status == AppointmentStatus.RESCHEDULED
    )
    rescheduled_result = await session.execute(rescheduled_query)
    rescheduled_appointments = rescheduled_result.scalar() or 0

    # Cancelled appointments
    cancelled_query = select(func.count(Appointment.id)).where(
        Appointment.status == AppointmentStatus.CANCELLED
    )
    cancelled_result = await session.execute(cancelled_query)
    cancelled_appointments = cancelled_result.scalar() or 0

    # Total patients
    patients_query = select(func.count(Patient.id))
    patients_result = await session.execute(patients_query)
    total_patients = patients_result.scalar() or 0

    # Active doctors
    doctors_query = select(func.count(Doctor.id)).where(Doctor.is_active == True)
    doctors_result = await session.execute(doctors_query)
    active_doctors = doctors_result.scalar() or 0

    return DashboardStats(
        total_appointments=total_appointments,
        appointments_today=appointments_today,
        pending_appointments=pending_appointments,
        confirmed_appointments=confirmed_appointments,
        rescheduled_appointments=rescheduled_appointments,
        cancelled_appointments=cancelled_appointments,
        total_patients=total_patients,
        active_doctors=active_doctors
    )
