"""
Script to create Cesar Duran Mella patient with pending appointment for real Twilio testing.
"""
import asyncio
from datetime import datetime, timedelta
from src.database.connection import get_session_factory
from src.database.repositories import PatientRepository, AppointmentRepository
from src.database.models import AppointmentStatus


async def create_cesar_patient():
    """Create Cesar Duran Mella patient with a pending appointment."""
    session_factory = get_session_factory()

    async with session_factory() as session:
        patient_repo = PatientRepository(session)
        appointment_repo = AppointmentRepository(session)

        # Patient details
        phone = "whatsapp:+56978754779"
        first_name = "Cesar"
        last_name = "Duran Mella"
        rut = "18765432-1"  # Example RUT
        email = "cesar.duran@example.com"

        # Check if patient already exists
        patient = await patient_repo.get_by_phone(phone)

        if patient:
            print(f"✓ Patient already exists: {patient.first_name} {patient.last_name} (ID: {patient.id})")
        else:
            # Create patient
            patient = await patient_repo.create(
                rut=rut,
                phone=phone,
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            print(f"✓ Created patient: {patient.first_name} {patient.last_name} (ID: {patient.id})")

        # Create a pending appointment for tomorrow
        appointment_date = datetime.now() + timedelta(days=1)
        appointment_date = appointment_date.replace(hour=14, minute=30, second=0, microsecond=0)

        # Check if there's already a pending appointment
        existing_appointment = await appointment_repo.get_pending_for_patient(patient.id)

        if existing_appointment:
            print(f"✓ Pending appointment already exists (ID: {existing_appointment.id})")
            print(f"  Date: {existing_appointment.appointment_date}")
            print(f"  Doctor: {existing_appointment.doctor_name}")
            print(f"  Status: {existing_appointment.status.value}")
        else:
            # Create new pending appointment
            appointment = await appointment_repo.create(
                patient_id=patient.id,
                appointment_date=appointment_date,
                doctor_name="Dr. Andrea Silva",
                specialty="Medicina General",
                notes="Cita creada para pruebas reales con Twilio"
            )
            await session.commit()
            print(f"✓ Created pending appointment (ID: {appointment.id})")
            print(f"  Date: {appointment.appointment_date}")
            print(f"  Doctor: {appointment.doctor_name}")
            print(f"  Specialty: {appointment.specialty}")

        print("\n" + "="*60)
        print("PATIENT READY FOR REAL TWILIO TESTING")
        print("="*60)
        print(f"Name: {patient.first_name} {patient.last_name}")
        print(f"Phone: {patient.phone}")
        print(f"WhatsApp Number: +56978754779")
        print("\nTo test, send a WhatsApp message from +56978754779 to your Twilio number:")
        print("- 'Confirmo' or 'Confirmo mi cita' → Should confirm the appointment")
        print("- 'Cancelo' or 'Cancelo mi cita' → Should cancel the appointment")
        print("- Any other message → Should get help instructions")
        print("="*60)


if __name__ == "__main__":
    asyncio.run(create_cesar_patient())
