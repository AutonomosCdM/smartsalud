"""
Script para crear slots de disponibilidad en Google Calendar.

Crea bloques de tiempo donde el doctor está disponible para citas.
"""
import sys
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.calendar.service import CalendarService


async def create_availability_slots():
    """
    Crear 3 slots de disponibilidad para mañana.

    Slots:
    - 15:00 - 16:00
    - 16:00 - 17:00
    - 17:00 - 18:00
    """
    print("=" * 70)
    print("CREANDO SLOTS DE DISPONIBILIDAD - Google Calendar")
    print("=" * 70)
    print()

    # Initialize calendar service
    calendar_service = CalendarService()

    if not calendar_service.service:
        print("❌ ERROR: Calendar service not initialized")
        print("   Run: python scripts/setup_google_calendar.py")
        return False

    print("✅ Calendar service initialized")
    print()

    # Calculate tomorrow's date
    tomorrow = datetime.now() + timedelta(days=1)

    # Create 3 availability slots
    slots = [
        {"start_hour": 15, "start_min": 0, "end_hour": 16, "end_min": 0},
        {"start_hour": 16, "start_min": 0, "end_hour": 17, "end_min": 0},
        {"start_hour": 17, "start_min": 0, "end_hour": 18, "end_min": 0},
    ]

    created_events = []

    for i, slot in enumerate(slots, 1):
        start_time = tomorrow.replace(
            hour=slot["start_hour"],
            minute=slot["start_min"],
            second=0,
            microsecond=0
        )
        end_time = tomorrow.replace(
            hour=slot["end_hour"],
            minute=slot["end_min"],
            second=0,
            microsecond=0
        )

        print(f"📅 Creando Slot {i}:")
        print(f"   Fecha: {start_time.strftime('%d/%m/%Y')}")
        print(f"   Hora: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")

        # Create event with blue color (available)
        event_id = await calendar_service.create_event(
            summary=f"🟢 Disponible - Slot {i}",
            start_time=start_time,
            end_time=end_time,
            description=f"Bloque de disponibilidad para citas médicas.\n\nDoctor disponible para atención.",
            status="PENDING",  # Will be blue/lavender
            calendar_id="primary"
        )

        if event_id:
            created_events.append({
                "slot": i,
                "event_id": event_id,
                "start": start_time,
                "end": end_time
            })
            print(f"   ✅ Creado: {event_id}")
        else:
            print(f"   ❌ Error al crear slot")

        print()

    # Summary
    print("=" * 70)
    print(f"✅ SLOTS CREADOS: {len(created_events)}/3")
    print("=" * 70)
    print()

    if created_events:
        print("📋 Resumen de slots creados:")
        print()
        for event in created_events:
            print(f"   Slot {event['slot']}: {event['start'].strftime('%d/%m/%Y %H:%M')} - {event['end'].strftime('%H:%M')}")
            print(f"   Event ID: {event['event_id']}")
            print()

        print("🔗 Ver en Google Calendar:")
        print(f"   https://calendar.google.com/calendar/u/0/r/day/{tomorrow.strftime('%Y/%m/%d')}")
        print()

    return len(created_events) == 3


if __name__ == '__main__':
    success = asyncio.run(create_availability_slots())
    sys.exit(0 if success else 1)
