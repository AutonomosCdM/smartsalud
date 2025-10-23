"""
REST API endpoints for patients management.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import Optional, List
import structlog

from src.database.connection import get_db
from src.database.models import Patient
from pydantic import BaseModel

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api", tags=["patients"])


# Pydantic models
class PatientResponse(BaseModel):
    id: int
    rut: str
    phone: str
    first_name: str
    last_name: str
    email: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/patients", response_model=List[PatientResponse])
async def list_patients(
    search: Optional[str] = Query(None, description="Search by name, RUT or phone"),
    limit: int = Query(50, le=100),
    session: AsyncSession = Depends(get_db)
):
    """
    List patients with optional search.
    
    - **search**: Search term for name, RUT or phone
    - **limit**: Maximum number of results (default 50, max 100)
    """
    query = select(Patient)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Patient.first_name.ilike(search_term),
                Patient.last_name.ilike(search_term),
                Patient.rut.ilike(search_term),
                Patient.phone.ilike(search_term)
            )
        )
    
    query = query.order_by(Patient.last_name, Patient.first_name).limit(limit)
    
    result = await session.execute(query)
    patients = result.scalars().all()
    
    return [PatientResponse.model_validate(patient) for patient in patients]


@router.get("/patients/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    session: AsyncSession = Depends(get_db)
):
    """Get a specific patient by ID."""
    patient = await session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return PatientResponse.model_validate(patient)
