"""
Cargar horarios reales de CESFAM Sector 1 y 2.

Basado en la imagen real de horarios:
- Lunes a Viernes
- 8:00 - 16:30
- Diferentes tipos de atención con duraciones específicas
"""
import sys
import asyncio
from pathlib import Path
from datetime import time as time_obj

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select
from src.database.connection import get_session_factory


async def load_real_schedule():
    """
    Cargar horarios reales del CESFAM Sector 1 y 2.
    """
    print("=" * 70)
    print("CARGANDO HORARIOS REALES - CESFAM SECTOR 1 Y 2")
    print("=" * 70)
    print()

    async_session_maker = get_session_factory()
    async with async_session_maker() as session:
        # 1. Crear doctor sintético (César)
        from sqlalchemy import text

        # Check if doctor exists
        result = await session.execute(
            text("SELECT id FROM doctors WHERE first_name = 'César' AND last_name = 'Durán'")
        )
        doctor = result.fetchone()

        if doctor:
            doctor_id = doctor[0]
            print(f"✅ Doctor César Durán ya existe (ID: {doctor_id})")
        else:
            # Create doctor
            result = await session.execute(
                text("""
                    INSERT INTO doctors (first_name, last_name, sector, specialty, calendar_email, is_active)
                    VALUES ('César', 'Durán', 'Sector 1 y 2', 'Medicina General', 'cesar@autonomos.dev', true)
                    RETURNING id
                """)
            )
            doctor_id = result.fetchone()[0]
            await session.commit()
            print(f"✅ Doctor César Durán creado (ID: {doctor_id})")

        print()

        # 2. Get appointment type IDs
        result = await session.execute(text("SELECT id, name FROM appointment_types"))
        appointment_types = {row[1]: row[0] for row in result.fetchall()}

        print("📋 Tipos de atención disponibles:")
        for name, type_id in appointment_types.items():
            print(f"   {type_id}: {name}")
        print()

        # 3. Define schedule based on real CESFAM data
        # Días 0-4 = Monday to Friday
        schedule_data = []

        for day in range(5):  # Monday to Friday
            # Mañana: 8:00 - 11:00 - Cons. Morbilidad (slots de 20 min)
            morning_slots = [
                (time_obj(8, 0), time_obj(8, 20)),
                (time_obj(8, 20), time_obj(8, 40)),
                (time_obj(8, 40), time_obj(9, 0)),
                (time_obj(9, 0), time_obj(9, 20)),
                (time_obj(9, 20), time_obj(9, 40)),
                (time_obj(9, 40), time_obj(10, 0)),
                (time_obj(10, 0), time_obj(10, 20)),
                (time_obj(10, 20), time_obj(10, 40))
            ]

            for start, end in morning_slots:
                schedule_data.append({
                    "day": day,
                    "start": start,
                    "end": end,
                    "type": "Cons. Morbilidad"
                })

            # Pausa saludable
            schedule_data.append({
                "day": day,
                "start": time_obj(10, 40),
                "end": time_obj(11, 0),
                "type": "Pausa Saludable"
            })

            # Salud Mental: 11:00 - 13:00 (slots de 40 min)
            schedule_data.extend([
                {"day": day, "start": time_obj(11, 0), "end": time_obj(11, 40), "type": "Salud Mental"},
                {"day": day, "start": time_obj(11, 40), "end": time_obj(12, 20), "type": "Salud Mental"},
                {"day": day, "start": time_obj(12, 20), "end": time_obj(13, 0), "type": "Salud Mental"}
            ])

            # Tarde: 14:00 - 16:00 - Control o crónico (slots de 30 min)
            afternoon_slots = [
                (time_obj(14, 0), time_obj(14, 30)),
                (time_obj(14, 30), time_obj(15, 0)),
                (time_obj(15, 0), time_obj(15, 30)),
                (time_obj(15, 30), time_obj(16, 0))
            ]

            for start, end in afternoon_slots:
                schedule_data.append({
                    "day": day,
                    "start": start,
                    "end": end,
                    "type": "Control o crónico"
                })

            # Recetas: 16:00 - 16:30
            schedule_data.append({
                "day": day,
                "start": time_obj(16, 0),
                "end": time_obj(16, 30),
                "type": "Recetas"
            })

        # 4. Clear existing schedules for this doctor
        await session.execute(
            text("DELETE FROM doctor_schedules WHERE doctor_id = :doctor_id"),
            {"doctor_id": doctor_id}
        )

        print(f"🗑️  Horarios anteriores eliminados")
        print()

        # 5. Insert new schedules
        print("📅 Insertando horarios...")
        inserted = 0

        for slot in schedule_data:
            type_id = appointment_types.get(slot["type"])
            if not type_id:
                print(f"⚠️  Tipo no encontrado: {slot['type']}")
                continue

            await session.execute(
                text("""
                    INSERT INTO doctor_schedules
                    (doctor_id, day_of_week, start_time, end_time, appointment_type_id, is_active)
                    VALUES (:doctor_id, :day, :start_time, :end_time, :type_id, true)
                """),
                {
                    "doctor_id": doctor_id,
                    "day": slot["day"],
                    "start_time": slot["start"],
                    "end_time": slot["end"],
                    "type_id": type_id
                }
            )
            inserted += 1

            if inserted % 10 == 0:
                print(f"   ✅ Insertados {inserted} slots...")

        await session.commit()

        print()
        print("=" * 70)
        print(f"✅ CARGA COMPLETA: {inserted} slots insertados")
        print("=" * 70)
        print()

        # 6. Summary
        result = await session.execute(
            text("""
                SELECT
                    at.name,
                    COUNT(*) as total_slots
                FROM doctor_schedules ds
                JOIN appointment_types at ON ds.appointment_type_id = at.id
                WHERE ds.doctor_id = :doctor_id
                GROUP BY at.name
                ORDER BY at.name
            """),
            {"doctor_id": doctor_id}
        )

        print("📊 Resumen por tipo de atención:")
        print()
        for row in result.fetchall():
            print(f"   {row[0]}: {row[1]} slots por semana ({row[1] * 20} slots por mes)")
        print()

        print("🎯 Próximos pasos:")
        print("   1. Ejecutar: python scripts/configure_calendar_view.py")
        print("   2. Configurar horarios de trabajo en Google Calendar (8:00-17:00)")
        print("   3. Modificar handlers para usar estos horarios reales")
        print()

        return True


if __name__ == '__main__':
    success = asyncio.run(load_real_schedule())
    sys.exit(0 if success else 1)
