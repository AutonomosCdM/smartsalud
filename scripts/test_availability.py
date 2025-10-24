"""
Script de prueba para el servicio de disponibilidad.

Verifica que el cálculo de slots disponibles funciona correctamente.
"""
import sys
import asyncio
from pathlib import Path
from datetime import date, timedelta

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.connection import get_session_factory
from src.services.availability_service import AvailabilityService


async def test_availability():
    """
    Prueba el servicio de disponibilidad con datos reales.
    """
    print("=" * 70)
    print("PRUEBA DE SERVICIO DE DISPONIBILIDAD")
    print("=" * 70)
    print()

    async_session_maker = get_session_factory()
    async with async_session_maker() as session:
        service = AvailabilityService(session)

        # Doctor César Durán (ID: 1)
        doctor_id = 1

        # Buscar slots para los próximos 7 días
        today = date.today()
        end_date = today + timedelta(days=7)

        print(f"📅 Buscando slots disponibles:")
        print(f"   Doctor ID: {doctor_id}")
        print(f"   Desde: {today}")
        print(f"   Hasta: {end_date}")
        print()

        # 1. Obtener todos los slots disponibles
        slots = await service.get_available_slots(
            doctor_id=doctor_id,
            start_date=today,
            end_date=end_date
        )

        print(f"✅ Encontrados {len(slots)} slots disponibles")
        print()

        # 2. Mostrar primeros 10 slots
        print("🕐 Primeros 10 slots disponibles:")
        for i, slot in enumerate(slots[:10], 1):
            print(f"   {i}. {slot.start_datetime.strftime('%Y-%m-%d %H:%M')} - "
                  f"{slot.end_datetime.strftime('%H:%M')} | "
                  f"{slot.appointment_type_name} ({slot.duration_minutes} min) | "
                  f"{slot.doctor_name}")
        print()

        # 3. Agrupar por tipo de atención
        by_type = {}
        for slot in slots:
            if slot.appointment_type_name not in by_type:
                by_type[slot.appointment_type_name] = 0
            by_type[slot.appointment_type_name] += 1

        print("📊 Slots por tipo de atención:")
        for type_name, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            print(f"   {type_name}: {count} slots")
        print()

        # 4. Agrupar por día
        by_day = {}
        for slot in slots:
            day_str = slot.start_datetime.strftime('%A %Y-%m-%d')
            if day_str not in by_day:
                by_day[day_str] = 0
            by_day[day_str] += 1

        print("📆 Slots por día:")
        for day_str, count in sorted(by_day.items()):
            print(f"   {day_str}: {count} slots")
        print()

        # 5. Buscar próximo slot disponible
        next_slot = await service.get_next_available_slot(
            doctor_id=doctor_id,
            days_ahead=30
        )

        if next_slot:
            print("⏭️  Próximo slot disponible:")
            print(f"   Fecha: {next_slot.start_datetime.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Tipo: {next_slot.appointment_type_name}")
            print(f"   Duración: {next_slot.duration_minutes} min")
            print(f"   Doctor: {next_slot.doctor_name}")
        else:
            print("❌ No hay slots disponibles en los próximos 30 días")

        print()
        print("=" * 70)
        print("✅ Prueba completada exitosamente")
        print("=" * 70)

    return True


if __name__ == '__main__':
    success = asyncio.run(test_availability())
    sys.exit(0 if success else 1)
