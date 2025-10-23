"""
Script para crear datos de prueba en la base de datos.

Crea:
- 1 paciente de prueba con número WhatsApp
- 1 cita pendiente para ese paciente
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_session_factory
from src.database.repositories import PatientRepository, AppointmentRepository


async def create_test_data():
    """Crear datos de prueba."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        patient_repo = PatientRepository(session)
        appointment_repo = AppointmentRepository(session)

        print("\n🔍 Buscando paciente de prueba...")

        # Buscar paciente existente
        test_phone = "whatsapp:+5691234"  # Shorter for VARCHAR(20) constraint
        patient = await patient_repo.get_by_phone(test_phone)

        if patient:
            print(f"✅ Paciente ya existe: {patient.first_name} {patient.last_name} (ID: {patient.id})")
        else:
            # Crear paciente de prueba
            print("\n📝 Creando paciente de prueba...")
            patient = await patient_repo.create(
                rut="12345678-9",
                phone=test_phone,
                first_name="María",
                last_name="González",
                email="maria.gonzalez@example.com"
            )
            print(f"✅ Paciente creado: {patient.first_name} {patient.last_name} (ID: {patient.id})")

        # Buscar cita pendiente
        print(f"\n🔍 Buscando cita pendiente para paciente {patient.id}...")
        pending_appointment = await appointment_repo.get_pending_for_patient(patient.id)

        if pending_appointment:
            print(f"✅ Ya existe cita pendiente:")
            print(f"   - ID: {pending_appointment.id}")
            print(f"   - Fecha: {pending_appointment.appointment_date.strftime('%d/%m/%Y %H:%M')}")
            print(f"   - Doctor: {pending_appointment.doctor_name}")
            print(f"   - Estado: {pending_appointment.status.value}")
        else:
            # Crear cita pendiente
            print("\n📝 Creando cita de prueba...")
            appointment_date = datetime.now() + timedelta(days=1, hours=10)  # Mañana a las 10 AM
            appointment = await appointment_repo.create(
                patient_id=patient.id,
                appointment_date=appointment_date,
                doctor_name="Dr. Roberto García",
                specialty="Medicina General",
                notes="Cita de prueba creada por script"
            )
            print(f"✅ Cita creada:")
            print(f"   - ID: {appointment.id}")
            print(f"   - Fecha: {appointment.appointment_date.strftime('%d/%m/%Y %H:%M')}")
            print(f"   - Doctor: {appointment.doctor_name}")
            print(f"   - Estado: {appointment.status.value}")

        await session.commit()

        print("\n" + "="*60)
        print("✅ DATOS DE PRUEBA LISTOS")
        print("="*60)
        print(f"\n📱 Número WhatsApp: {test_phone}")
        print(f"👤 Paciente: {patient.first_name} {patient.last_name}")
        print(f"🆔 Patient ID: {patient.id}")

        # Obtener la cita actual
        current_appointment = await appointment_repo.get_pending_for_patient(patient.id)
        if current_appointment:
            print(f"📅 Cita pendiente: {current_appointment.appointment_date.strftime('%d/%m/%Y %H:%M')}")
            print(f"🩺 Doctor: {current_appointment.doctor_name}")
            print(f"📊 Estado: {current_appointment.status.value}")

        print("\n📨 Prueba el webhook con:")
        print(f"""
curl -X POST http://localhost:8001/api/webhook/whatsapp \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "From={test_phone}" \\
  -d "Body=Confirmo" \\
  -d "MessageSid=TEST123456789"
        """)


if __name__ == "__main__":
    asyncio.run(create_test_data())
