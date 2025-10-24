"""
Seed production database with real patient and appointment data.

Run with production DATABASE_URL:
    DATABASE_URL=<production_url> python scripts/seed_production_data.py
"""
import asyncio
import os
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.database.models import Patient, Appointment, AppointmentStatus


async def seed_data():
    """Seed production database with initial data."""
    # Get production database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return

    # Convert to asyncpg if needed
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

    print(f"🔗 Connecting to database...")
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("📝 Creating patients and appointments...")

        # Paciente 1: Patricio Contreras - Cita el Lunes 27/10
        patient1 = Patient(
            rut="12345678-9",
            phone="whatsapp:+56927699018",
            first_name="Patricio",
            last_name="Contreras",
            email="patricio.contreras@example.com"
        )
        session.add(patient1)
        await session.flush()

        appointment1 = Appointment(
            patient_id=patient1.id,
            appointment_date=datetime(2025, 10, 27, 10, 0),  # Lunes 27/10 a las 10:00
            doctor_name="Dra. Aimee Rodriguez",
            specialty="Medicina General",
            status=AppointmentStatus.PENDING
        )
        session.add(appointment1)

        # Paciente 2: Sandra Castillo - Cita el Martes 28/10
        patient2 = Patient(
            rut="98765432-1",
            phone="whatsapp:+56997495593",
            first_name="Sandra",
            last_name="Castillo",
            email="sandra.castillo@example.com"
        )
        session.add(patient2)
        await session.flush()

        appointment2 = Appointment(
            patient_id=patient2.id,
            appointment_date=datetime(2025, 10, 28, 14, 30),  # Martes 28/10 a las 14:30
            doctor_name="Dra. Constanza Canelo",
            specialty="Medicina General",
            status=AppointmentStatus.PENDING
        )
        session.add(appointment2)

        # Paciente 3: Americo Gonzales (sin cita aún)
        patient3 = Patient(
            rut="11223344-5",
            phone="whatsapp:+56976486175",
            first_name="Americo",
            last_name="Gonzales",
            email="americo.gonzales@example.com"
        )
        session.add(patient3)

        # Paciente 4: Claudio (sin cita aún)
        patient4 = Patient(
            rut="55667788-9",
            phone="whatsapp:+56949781566",
            first_name="Claudio",
            last_name="González",
            email="claudio.gonzalez@example.com"
        )
        session.add(patient4)

        await session.commit()

        print("✅ Data seeded successfully!")
        print("\n📋 Summary:")
        print(f"  - {patient1.first_name} {patient1.last_name} ({patient1.phone})")
        print(f"    → Cita: {appointment1.appointment_date.strftime('%d/%m/%Y %H:%M')} con {appointment1.doctor_name}")
        print(f"  - {patient2.first_name} {patient2.last_name} ({patient2.phone})")
        print(f"    → Cita: {appointment2.appointment_date.strftime('%d/%m/%Y %H:%M')} con {appointment2.doctor_name}")
        print(f"  - {patient3.first_name} {patient3.last_name} ({patient3.phone}) - Sin cita")
        print(f"  - {patient4.first_name} {patient4.last_name} ({patient4.phone}) - Sin cita")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_data())
