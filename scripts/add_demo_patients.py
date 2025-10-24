"""
Agregar pacientes de demo para prueba de agente de voz
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select

from src.database.connection import get_session_factory
from src.database.models import Patient, Appointment, Doctor, AppointmentType


async def add_demo_patients():
    """Agregar pacientes de demo con citas"""

    session_factory = get_session_factory()
    async with session_factory() as session:
        # 1. Get any active doctor
        result = await session.execute(
            select(Doctor).where(Doctor.is_active == True).limit(1)
        )
        doctor = result.scalar_one_or_none()

        if not doctor:
            print("❌ No hay doctores activos. Ejecuta primero scripts/load_real_schedule.py")
            return

        print(f"✅ Usando doctor: {doctor.name} ({doctor.specialty})")

        # 2. Get any appointment type
        result = await session.execute(
            select(AppointmentType).limit(1)
        )
        apt_type = result.scalar_one_or_none()

        if not apt_type:
            print("❌ No hay tipos de cita. Ejecuta primero scripts/load_real_schedule.py")
            return

        print(f"✅ Usando tipo de cita: {apt_type.name} ({apt_type.duration_minutes} min)")

        # 3. Demo patients data
        demo_patients = [
            {
                "rut": "11111111-1",
                "first_name": "Sandra",
                "last_name": "Castillo",
                "phone": "+56997495593",
                "email": "sandra.castillo@example.com",
            },
            {
                "rut": "22222222-2",
                "first_name": "Americo",
                "last_name": "Gonzales",
                "phone": "+56976486175",
                "email": "americo.gonzales@example.com",
            },
            {
                "rut": "33333333-3",
                "first_name": "Patricio",
                "last_name": "Contreras",
                "phone": "+56927699018",
                "email": "patricio.contreras@example.com",
            },
        ]

        # 4. Insert patients and create appointments
        tomorrow = datetime.now() + timedelta(days=1)
        base_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)

        for idx, patient_data in enumerate(demo_patients):
            # Check if patient already exists
            result = await session.execute(
                select(Patient).where(Patient.rut == patient_data["rut"])
            )
            patient = result.scalar_one_or_none()

            if patient:
                print(f"✅ Paciente {patient_data['first_name']} {patient_data['last_name']} ya existe")
            else:
                # Create patient
                patient = Patient(**patient_data)
                session.add(patient)
                await session.flush()
                print(f"✅ Creado paciente: {patient.first_name} {patient.last_name}")

            # Create appointment for tomorrow
            appointment_time = base_time + timedelta(hours=idx * 2)  # 10:00, 12:00, 14:00

            # Check if appointment already exists
            result = await session.execute(
                select(Appointment).where(
                    Appointment.patient_id == patient.id,
                    Appointment.appointment_date == appointment_time,
                    Appointment.status == "PENDING"
                )
            )
            existing_apt = result.scalar_one_or_none()

            if not existing_apt:
                appointment = Appointment(
                    patient_id=patient.id,
                    doctor_id=doctor.id,
                    appointment_type_id=apt_type.id,
                    appointment_date=appointment_time,
                    doctor_name=doctor.name,
                    specialty=doctor.specialty,
                    status="PENDING",
                    notes=f"Cita de demo para prueba de agente de voz"
                )
                session.add(appointment)
                print(f"   📅 Cita creada: {appointment_time.strftime('%d/%m/%Y %H:%M')}")
            else:
                print(f"   📅 Cita ya existe: {appointment_time.strftime('%d/%m/%Y %H:%M')}")

        await session.commit()
        print("\n✅ Pacientes de demo agregados correctamente!")
        print(f"\n📱 Los pacientes pueden probar el agente con estos RUTs:")
        for p in demo_patients:
            print(f"   - {p['first_name']} {p['last_name']}: {p['rut']} ({p['phone']})")


if __name__ == "__main__":
    asyncio.run(add_demo_patients())
