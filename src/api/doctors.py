"""
REST API endpoints for doctors and availability.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date, datetime, time
from typing import List
import structlog

from src.database.connection import get_db
from src.database.models import Doctor, AppointmentType
from src.services.availability_service_v2 import AvailabilityServiceV2
from pydantic import BaseModel

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api", tags=["doctors"])


# Pydantic models
class DoctorResponse(BaseModel):
    id: int
    name: str
    sector: str
    specialty: str
    calendar_email: str | None

    class Config:
        from_attributes = True


class TimeSlotResponse(BaseModel):
    start_time: datetime
    end_time: datetime
    is_available: bool
    appointment_type_id: int
    appointment_type_name: str
    duration_minutes: int


@router.get("/doctors", response_model=List[DoctorResponse])
async def list_doctors(
    session: AsyncSession = Depends(get_db)
):
    """List all doctors."""
    query = select(Doctor).order_by(Doctor.first_name, Doctor.last_name)
    result = await session.execute(query)
    doctors = result.scalars().all()

    return [DoctorResponse.model_validate(doctor) for doctor in doctors]


@router.get("/doctors/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(
    doctor_id: int,
    session: AsyncSession = Depends(get_db)
):
    """Get a specific doctor by ID."""
    doctor = await session.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return DoctorResponse.model_validate(doctor)


@router.get("/doctors/{doctor_id}/availability", response_model=List[TimeSlotResponse])
async def get_doctor_availability(
    doctor_id: int,
    target_date: date = Query(..., description="Date to check availability (YYYY-MM-DD)"),
    appointment_type_id: int = Query(..., description="Appointment type ID"),
    session: AsyncSession = Depends(get_db)
):
    """
    Get available time slots for a doctor on a specific date.
    
    - **doctor_id**: The doctor's ID
    - **target_date**: Date to check (YYYY-MM-DD)
    - **appointment_type_id**: Type of appointment to book
    """
    # Verify doctor exists
    doctor = await session.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Verify appointment type exists
    apt_type = await session.get(AppointmentType, appointment_type_id)
    if not apt_type:
        raise HTTPException(status_code=404, detail="Appointment type not found")
    
    # Get availability
    availability_service = AvailabilityServiceV2(session)

    try:
        available_slots = await availability_service.get_available_slots(
            doctor_id=doctor_id,
            start_date=target_date,
            end_date=target_date,
            appointment_type_id=appointment_type_id
        )
        
        # Convert to response format
        response = []
        for slot in available_slots:
            response.append(TimeSlotResponse(
                start_time=slot.start_datetime,
                end_time=slot.end_datetime,
                is_available=True,
                appointment_type_id=appointment_type_id,
                appointment_type_name=apt_type.name,
                duration_minutes=apt_type.duration_minutes
            ))
        
        logger.info(
            "availability_fetched",
            doctor_id=doctor_id,
            date=str(target_date),
            slots_count=len(response)
        )
        
        return response
        
    except Exception as e:
        logger.error("availability_fetch_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch availability")


@router.get("/appointment-types", response_model=List[dict])
async def list_appointment_types(
    session: AsyncSession = Depends(get_db)
):
    """List all appointment types."""
    query = select(AppointmentType).order_by(AppointmentType.name)
    result = await session.execute(query)
    types = result.scalars().all()
    
    return [
        {
            "id": t.id,
            "name": t.name,
            "duration_minutes": t.duration_minutes,
            "color": t.color
        }
        for t in types
    ]
