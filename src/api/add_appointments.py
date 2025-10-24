"""
Temporary endpoint to add appointments for all patients.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import structlog

from src.api.dependencies import get_db
from src.database.models import Appointment, AppointmentStatus
from src.database.repositories import PatientRepository

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api", tags=["admin"])


@router.post("/add-appointments")
async def add_appointments(db: AsyncSession = Depends(get_db)):
    """
    Add appointments for patients without appointments.

    Creates 5 new appointments for:
    - Americo Gonzales
    - Claudio González
    - Cesar Duran
    - Ramon Roa
    - Tamara Aguilera

    Returns:
        Summary of created appointments
    """
    try:
        logger.info("add_appointments_started")

        patient_repo = PatientRepository(db)

        # Get patients by phone
        americo = await patient_repo.get_by_phone("whatsapp:+56976486175")
        claudio = await patient_repo.get_by_phone("whatsapp:+56949781566")
        cesar = await patient_repo.get_by_phone("whatsapp:+56978754779")
        ramon = await patient_repo.get_by_phone("whatsapp:+56996645517")
        tamara = await patient_repo.get_by_phone("whatsapp:+56982467078")

        if not all([americo, claudio, cesar, ramon, tamara]):
            logger.error("missing_patients")
            return {
                "status": "error",
                "message": "Some patients not found in database"
            }

        appointments = []

        # Americo Gonzales - Miércoles 29/10 a las 09:30 con Dr. Juan Castellanos
        appt1 = Appointment(
            patient_id=americo.id,
            appointment_date=datetime(2025, 10, 29, 9, 30),
            doctor_name="Dr. Juan Castellanos",
            specialty="Medicina General",
            status=AppointmentStatus.PENDING
        )
        db.add(appt1)
        appointments.append({
            "patient": f"{americo.first_name} {americo.last_name}",
            "phone": americo.phone,
            "date": "29/10/2025 09:30",
            "doctor": "Dr. Juan Castellanos"
        })

        # Claudio González - Jueves 30/10 a las 11:00 con Jordi Opazo (Kinesiólogo)
        appt2 = Appointment(
            patient_id=claudio.id,
            appointment_date=datetime(2025, 10, 30, 11, 0),
            doctor_name="Jordi Opazo",
            specialty="Kinesiología",
            status=AppointmentStatus.PENDING
        )
        db.add(appt2)
        appointments.append({
            "patient": f"{claudio.first_name} {claudio.last_name}",
            "phone": claudio.phone,
            "date": "30/10/2025 11:00",
            "doctor": "Jordi Opazo (Kinesiología)"
        })

        # Cesar Duran - Viernes 31/10 a las 15:00 con Dra. Rayen Gonzalez
        appt3 = Appointment(
            patient_id=cesar.id,
            appointment_date=datetime(2025, 10, 31, 15, 0),
            doctor_name="Dra. Rayen Gonzalez",
            specialty="Medicina General",
            status=AppointmentStatus.PENDING
        )
        db.add(appt3)
        appointments.append({
            "patient": f"{cesar.first_name} {cesar.last_name}",
            "phone": cesar.phone,
            "date": "31/10/2025 15:00",
            "doctor": "Dra. Rayen Gonzalez"
        })

        # Ramon Roa - Lunes 03/11 a las 10:30 con Daniela Iceta (Nutricionista)
        appt4 = Appointment(
            patient_id=ramon.id,
            appointment_date=datetime(2025, 11, 3, 10, 30),
            doctor_name="Daniela Iceta",
            specialty="Nutrición",
            status=AppointmentStatus.PENDING
        )
        db.add(appt4)
        appointments.append({
            "patient": f"{ramon.first_name} {ramon.last_name}",
            "phone": ramon.phone,
            "date": "03/11/2025 10:30",
            "doctor": "Daniela Iceta (Nutrición)"
        })

        # Tamara Aguilera - Martes 04/11 a las 14:00 con Enf. Yonathan Mansilla
        appt5 = Appointment(
            patient_id=tamara.id,
            appointment_date=datetime(2025, 11, 4, 14, 0),
            doctor_name="Enf. Yonathan Mansilla",
            specialty="Enfermería",
            status=AppointmentStatus.PENDING
        )
        db.add(appt5)
        appointments.append({
            "patient": f"{tamara.first_name} {tamara.last_name}",
            "phone": tamara.phone,
            "date": "04/11/2025 14:00",
            "doctor": "Enf. Yonathan Mansilla"
        })

        await db.commit()

        logger.info("add_appointments_completed", appointments=5)

        return {
            "status": "success",
            "message": "5 appointments created successfully",
            "appointments": appointments
        }

    except Exception as e:
        logger.error("add_appointments_failed", error=str(e), exc_info=True)
        await db.rollback()
        return {
            "status": "error",
            "message": f"Failed to create appointments: {str(e)}"
        }
