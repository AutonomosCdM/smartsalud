"""
Verificar horarios cargados en la base de datos.
"""
import sys
import asyncio
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from src.database.connection import get_session_factory


async def verify_schedule():
    """
    Verificar horarios cargados.
    """
    print("=" * 70)
    print("VERIFICACIÓN DE HORARIOS CARGADOS")
    print("=" * 70)
    print()

    async_session_maker = get_session_factory()
    async with async_session_maker() as session:
        # Doctor info
        result = await session.execute(
            text("SELECT id, first_name, last_name, sector, specialty FROM doctors")
        )
        doctors = result.fetchall()

        print("👨‍⚕️ Doctores registrados:")
        for doc in doctors:
            print(f"   ID: {doc[0]} - {doc[1]} {doc[2]} - {doc[3]} - {doc[4]}")
        print()

        # Schedule summary by day
        result = await session.execute(
            text("""
                SELECT
                    day_of_week,
                    COUNT(*) as total_slots
                FROM doctor_schedules
                WHERE doctor_id = 1
                GROUP BY day_of_week
                ORDER BY day_of_week
            """)
        )

        days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        print("📅 Slots por día:")
        for row in result.fetchall():
            print(f"   {days[row[0]]}: {row[1]} slots")
        print()

        # Schedule by appointment type
        result = await session.execute(
            text("""
                SELECT
                    at.name,
                    COUNT(*) as total_slots,
                    at.duration_minutes
                FROM doctor_schedules ds
                JOIN appointment_types at ON ds.appointment_type_id = at.id
                WHERE ds.doctor_id = 1
                GROUP BY at.name, at.duration_minutes
                ORDER BY at.name
            """)
        )

        print("📊 Slots por tipo de atención:")
        for row in result.fetchall():
            print(f"   {row[0]}: {row[1]} slots/semana ({row[2]} min cada uno)")
        print()

        # Sample schedule for Monday
        result = await session.execute(
            text("""
                SELECT
                    ds.start_time,
                    ds.end_time,
                    at.name
                FROM doctor_schedules ds
                JOIN appointment_types at ON ds.appointment_type_id = at.id
                WHERE ds.doctor_id = 1 AND ds.day_of_week = 0
                ORDER BY ds.start_time
                LIMIT 10
            """)
        )

        print("🕐 Primeros 10 slots del Lunes:")
        for row in result.fetchall():
            print(f"   {row[0]} - {row[1]}: {row[2]}")
        print()

        print("=" * 70)
        print("✅ Verificación completa")
        print("=" * 70)

    return True


if __name__ == '__main__':
    success = asyncio.run(verify_schedule())
    sys.exit(0 if success else 1)
