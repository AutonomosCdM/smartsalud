"""
Seed endpoint for populating database with initial data.

TEMPORARY: Used for initial production setup only.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import structlog

from src.api.dependencies import get_db
from src.database.models import Patient, Appointment, AppointmentStatus

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api", tags=["seed"])


@router.post("/seed")
async def seed_database(db: AsyncSession = Depends(get_db)):
    """
    Seed database with initial patient and appointment data.

    Creates:
    - 4 patients (Patricio, Sandra, Americo, Claudio)
    - 2 appointments (for Patricio and Sandra)

    Returns:
        Summary of created records
    """
    try:
        logger.info("seed_database_started")

        # Check if data already exists
        from src.database.repositories import PatientRepository
        patient_repo = PatientRepository(db)

        existing_patient = await patient_repo.get_by_phone("whatsapp:+56927699018")
        if existing_patient:
            logger.warning("seed_database_already_exists")
            return {
                "status": "skipped",
                "message": "Database already has data (found patient with phone +56927699018)"
            }

        # Paciente 1: Patricio Contreras - Cita el Lunes 27/10
        patient1 = Patient(
            rut="12345678-9",
            phone="whatsapp:+56927699018",
            first_name="Patricio",
            last_name="Contreras",
            email="patricio.contreras@example.com"
        )
        db.add(patient1)
        await db.flush()

        appointment1 = Appointment(
            patient_id=patient1.id,
            appointment_date=datetime(2025, 10, 27, 10, 0),  # Lunes 27/10 a las 10:00
            doctor_name="Dra. Aimee Rodriguez",
            specialty="Medicina General",
            status=AppointmentStatus.PENDING
        )
        db.add(appointment1)

        # Paciente 2: Sandra Castillo - Cita el Martes 28/10
        patient2 = Patient(
            rut="98765432-1",
            phone="whatsapp:+56997495593",
            first_name="Sandra",
            last_name="Castillo",
            email="sandra.castillo@example.com"
        )
        db.add(patient2)
        await db.flush()

        appointment2 = Appointment(
            patient_id=patient2.id,
            appointment_date=datetime(2025, 10, 28, 14, 30),  # Martes 28/10 a las 14:30
            doctor_name="Dra. Constanza Canelo",
            specialty="Medicina General",
            status=AppointmentStatus.PENDING
        )
        db.add(appointment2)

        # Paciente 3: Americo Gonzales (sin cita aún)
        patient3 = Patient(
            rut="11223344-5",
            phone="whatsapp:+56976486175",
            first_name="Americo",
            last_name="Gonzales",
            email="americo.gonzales@example.com"
        )
        db.add(patient3)

        # Paciente 4: Claudio (sin cita aún)
        patient4 = Patient(
            rut="55667788-9",
            phone="whatsapp:+56949781566",
            first_name="Claudio",
            last_name="González",
            email="claudio.gonzalez@example.com"
        )
        db.add(patient4)

        # Paciente 5: Cesar Duran (sin cita aún)
        patient5 = Patient(
            rut="22334455-6",
            phone="whatsapp:+56978754779",
            first_name="Cesar",
            last_name="Duran",
            email="cesar.duran@example.com"
        )
        db.add(patient5)

        # Paciente 6: Ramon Roa (sin cita aún)
        patient6 = Patient(
            rut="33445566-7",
            phone="whatsapp:+56996645517",
            first_name="Ramon",
            last_name="Roa",
            email="ramon.roa@example.com"
        )
        db.add(patient6)

        # Paciente 7: Tamara Aguilera (sin cita aún)
        patient7 = Patient(
            rut="44556677-8",
            phone="whatsapp:+56982467078",
            first_name="Tamara",
            last_name="Aguilera",
            email="tamara.aguilera@example.com"
        )
        db.add(patient7)

        await db.commit()

        logger.info("seed_database_completed", patients=7, appointments=2)

        return {
            "status": "success",
            "message": "Database seeded successfully",
            "patients_created": 7,
            "appointments_created": 2,
            "data": [
                {
                    "patient": f"{patient1.first_name} {patient1.last_name}",
                    "phone": patient1.phone,
                    "appointment": f"{appointment1.appointment_date.strftime('%d/%m/%Y %H:%M')} con {appointment1.doctor_name}"
                },
                {
                    "patient": f"{patient2.first_name} {patient2.last_name}",
                    "phone": patient2.phone,
                    "appointment": f"{appointment2.appointment_date.strftime('%d/%m/%Y %H:%M')} con {appointment2.doctor_name}"
                },
                {
                    "patient": f"{patient3.first_name} {patient3.last_name}",
                    "phone": patient3.phone,
                    "appointment": "Sin cita"
                },
                {
                    "patient": f"{patient4.first_name} {patient4.last_name}",
                    "phone": patient4.phone,
                    "appointment": "Sin cita"
                },
                {
                    "patient": f"{patient5.first_name} {patient5.last_name}",
                    "phone": patient5.phone,
                    "appointment": "Sin cita"
                },
                {
                    "patient": f"{patient6.first_name} {patient6.last_name}",
                    "phone": patient6.phone,
                    "appointment": "Sin cita"
                },
                {
                    "patient": f"{patient7.first_name} {patient7.last_name}",
                    "phone": patient7.phone,
                    "appointment": "Sin cita"
                }
            ]
        }

    except Exception as e:
        logger.error("seed_database_failed", error=str(e), exc_info=True)
        await db.rollback()
        return {
            "status": "error",
            "message": f"Failed to seed database: {str(e)}"
        }
