"""
Agregar 3 doctores más al sistema
"""
import asyncio
from sqlalchemy import select

from src.database.connection import get_session_factory
from src.database.models import Doctor


async def add_doctors():
    """Agregar 3 doctores más"""

    doctors_data = [
        {
            "first_name": "María",
            "last_name": "González",
            "sector": "Sector 1",
            "specialty": "Medicina Familiar",
        },
        {
            "first_name": "Pedro",
            "last_name": "Ramírez",
            "sector": "Sector 2",
            "specialty": "Pediatría",
        },
        {
            "first_name": "Ana",
            "last_name": "Torres",
            "sector": "Sector 3",
            "specialty": "Ginecología",
        },
    ]

    session_factory = get_session_factory()
    async with session_factory() as session:
        for doc_data in doctors_data:
            # Check if exists
            result = await session.execute(
                select(Doctor).where(
                    Doctor.first_name == doc_data["first_name"],
                    Doctor.last_name == doc_data["last_name"]
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"✅ Dr(a). {existing.name} ya existe")
                continue

            # Create doctor
            doctor = Doctor(
                first_name=doc_data["first_name"],
                last_name=doc_data["last_name"],
                sector=doc_data["sector"],
                specialty=doc_data["specialty"],
                is_active=True
            )
            session.add(doctor)
            await session.flush()
            print(f"✅ Creado: Dr(a). {doctor.name} - {doctor.specialty}")

        await session.commit()
        print("\n✅ Doctores agregados!")


if __name__ == "__main__":
    asyncio.run(add_doctors())
