"""
REST API endpoints for appointments management.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date, datetime, time, timedelta
from typing import Optional, List
import structlog

from src.database.connection import get_db
from src.database.models import Appointment, Patient, Doctor, AppointmentType
from src.services.booking_service import BookingService
from src.services.availability_service_v2 import AvailabilityServiceV2
from pydantic import BaseModel

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api", tags=["appointments"])


# Pydantic models for request/response
class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_type_id: int
    appointment_date: datetime
    notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: Optional[str] = None
    doctor_id: int
    doctor_name: str
    appointment_type_id: int
    appointment_type_name: str
    appointment_date: datetime
    status: str
    duration_minutes: int
    notes: Optional[str] = None
    calendar_event_id: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/appointments", response_model=List[AppointmentResponse])
async def list_appointments(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    doctor_id: Optional[int] = None,
    status: Optional[str] = None,
    session: AsyncSession = Depends(get_db)
):
    """
    List appointments with optional filters.
    
    - **start_date**: Filter appointments from this date
    - **end_date**: Filter appointments until this date
    - **doctor_id**: Filter by doctor
    - **status**: Filter by status (PENDING, CONFIRMED, CANCELLED, etc.)
    """
    query = (
        select(Appointment)
        .join(Doctor)
        .join(AppointmentType)
        .outerjoin(Patient)
    )
    
    # Apply filters
    if start_date:
        query = query.filter(Appointment.appointment_date >= datetime.combine(start_date, time.min))
    if end_date:
        query = query.filter(Appointment.appointment_date <= datetime.combine(end_date, time.max))
    if doctor_id:
        query = query.filter(Appointment.doctor_id == doctor_id)
    if status:
        query = query.filter(Appointment.status == status)
    
    # Order by date
    query = query.order_by(Appointment.appointment_date)
    
    result = await session.execute(query)
    appointments = result.scalars().all()
    
    # Build response
    response = []
    for apt in appointments:
        # Fetch related objects
        doctor = await session.get(Doctor, apt.doctor_id)
        apt_type = await session.get(AppointmentType, apt.appointment_type_id)
        patient = await session.get(Patient, apt.patient_id) if apt.patient_id else None
        
        response.append(AppointmentResponse(
            id=apt.id,
            patient_id=apt.patient_id,
            patient_name=f"{patient.first_name} {patient.last_name}" if patient else None,
            doctor_id=apt.doctor_id,
            doctor_name=doctor.name,
            appointment_type_id=apt.appointment_type_id,
            appointment_type_name=apt_type.name,
            appointment_date=apt.appointment_date,
            status=apt.status,
            duration_minutes=apt_type.duration_minutes,
            notes=apt.notes,
            calendar_event_id=apt.calendar_event_id
        ))
    
    return response


@router.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    session: AsyncSession = Depends(get_db)
):
    """Get a specific appointment by ID."""
    appointment = await session.get(Appointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Fetch related objects
    doctor = await session.get(Doctor, appointment.doctor_id)
    apt_type = await session.get(AppointmentType, appointment.appointment_type_id)
    patient = await session.get(Patient, appointment.patient_id) if appointment.patient_id else None
    
    return AppointmentResponse(
        id=appointment.id,
        patient_id=appointment.patient_id,
        patient_name=f"{patient.first_name} {patient.last_name}" if patient else None,
        doctor_id=appointment.doctor_id,
        doctor_name=doctor.name,
        appointment_type_id=appointment.appointment_type_id,
        appointment_type_name=apt_type.name,
        appointment_date=appointment.appointment_date,
        status=appointment.status,
        duration_minutes=apt_type.duration_minutes,
        notes=appointment.notes,
        calendar_event_id=appointment.calendar_event_id
    )


@router.post("/appointments", response_model=AppointmentResponse, status_code=201)
async def create_appointment(
    appointment_data: AppointmentCreate,
    session: AsyncSession = Depends(get_db)
):
    """
    Create a new appointment.
    
    Automatically syncs to doctor's Google Calendar via BookingService.
    """
    booking_service = BookingService(session)
    
    try:
        # Create appointment via BookingService (handles overlap detection + calendar sync)
        appointment = await booking_service.create_appointment(
            patient_id=appointment_data.patient_id,
            doctor_id=appointment_data.doctor_id,
            appointment_type_id=appointment_data.appointment_type_id,
            appointment_date=appointment_data.appointment_date,
            notes=appointment_data.notes
        )
        
        # Fetch related objects for response
        doctor = await session.get(Doctor, appointment.doctor_id)
        apt_type = await session.get(AppointmentType, appointment.appointment_type_id)
        patient = await session.get(Patient, appointment.patient_id) if appointment.patient_id else None
        
        logger.info(
            "appointment_created_via_api",
            appointment_id=appointment.id,
            doctor_id=appointment.doctor_id,
            calendar_event_id=appointment.calendar_event_id
        )
        
        return AppointmentResponse(
            id=appointment.id,
            patient_id=appointment.patient_id,
            patient_name=f"{patient.first_name} {patient.last_name}" if patient else None,
            doctor_id=appointment.doctor_id,
            doctor_name=doctor.name,
            appointment_type_id=appointment.appointment_type_id,
            appointment_type_name=apt_type.name,
            appointment_date=appointment.appointment_date,
            status=appointment.status,
            duration_minutes=apt_type.duration_minutes,
            notes=appointment.notes,
            calendar_event_id=appointment.calendar_event_id
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("appointment_creation_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create appointment")


@router.delete("/appointments/{appointment_id}")
async def cancel_appointment(
    appointment_id: int,
    session: AsyncSession = Depends(get_db)
):
    """Cancel an appointment and update calendar."""
    booking_service = BookingService(session)
    
    try:
        await booking_service.cancel_appointment(appointment_id)
        return {"message": "Appointment cancelled successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("appointment_cancellation_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to cancel appointment")
