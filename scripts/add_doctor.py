"""
Agregar doctor Jordi Opazo
"""
import asyncio
from sqlalchemy import select

from src.database.connection import get_session_factory
from src.database.models import Doctor


async def add_doctor():
    """Agregar Dr. Jordi Opazo Kinesiólogo"""

    session_factory = get_session_factory()
    async with session_factory() as session:
        # Check if doctor already exists
        result = await session.execute(
            select(Doctor).where(
                Doctor.first_name == "Jordi",
                Doctor.last_name == "Opazo"
            )
        )
        existing_doctor = result.scalar_one_or_none()

        if existing_doctor:
            print(f"✅ Doctor {existing_doctor.name} ya existe (ID: {existing_doctor.id})")
            return

        # Create new doctor
        doctor = Doctor(
            first_name="Jordi",
            last_name="Opazo",
            sector="CESFAM",
            specialty="Kinesiología",
            calendar_email=None,  # No calendar integration for now
            is_active=True
        )
        session.add(doctor)
        await session.commit()

        print(f"✅ Doctor agregado exitosamente!")
        print(f"   Nombre: {doctor.name}")
        print(f"   Especialidad: {doctor.specialty}")
        print(f"   ID: {doctor.id}")


if __name__ == "__main__":
    asyncio.run(add_doctor())
