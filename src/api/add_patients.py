"""
Temporary endpoint to add additional patients.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.api.dependencies import get_db
from src.database.models import Patient

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api", tags=["admin"])


@router.post("/add-patients")
async def add_patients(db: AsyncSession = Depends(get_db)):
    """
    Add 3 additional patients to the database.

    Returns:
        Summary of created patients
    """
    try:
        logger.info("add_patients_started")

        # Check if Cesar already exists
        from src.database.repositories import PatientRepository
        patient_repo = PatientRepository(db)

        existing = await patient_repo.get_by_phone("whatsapp:+56978754779")
        if existing:
            logger.warning("patients_already_exist")
            return {
                "status": "skipped",
                "message": "Patients already exist"
            }

        # Paciente 5: Cesar Duran
        patient5 = Patient(
            rut="22334455-6",
            phone="whatsapp:+56978754779",
            first_name="Cesar",
            last_name="Duran",
            email="cesar.duran@example.com"
        )
        db.add(patient5)

        # Paciente 6: Ramon Roa
        patient6 = Patient(
            rut="33445566-7",
            phone="whatsapp:+56996645517",
            first_name="Ramon",
            last_name="Roa",
            email="ramon.roa@example.com"
        )
        db.add(patient6)

        # Paciente 7: Tamara Aguilera
        patient7 = Patient(
            rut="44556677-8",
            phone="whatsapp:+56982467078",
            first_name="Tamara",
            last_name="Aguilera",
            email="tamara.aguilera@example.com"
        )
        db.add(patient7)

        await db.commit()

        logger.info("add_patients_completed", patients=3)

        return {
            "status": "success",
            "message": "3 patients added successfully",
            "patients": [
                {
                    "name": f"{patient5.first_name} {patient5.last_name}",
                    "phone": patient5.phone
                },
                {
                    "name": f"{patient6.first_name} {patient6.last_name}",
                    "phone": patient6.phone
                },
                {
                    "name": f"{patient7.first_name} {patient7.last_name}",
                    "phone": patient7.phone
                }
            ]
        }

    except Exception as e:
        logger.error("add_patients_failed", error=str(e), exc_info=True)
        await db.rollback()
        return {
            "status": "error",
            "message": f"Failed to add patients: {str(e)}"
        }
