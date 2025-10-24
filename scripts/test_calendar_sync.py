"""
Script de prueba para sincronización DB → Google Calendar.

Prueba el flujo completo de booking con sincronización automática.
"""
import sys
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.connection import get_session_factory
from src.services.booking_service import BookingService


async def test_calendar_sync():
    """
    Prueba la sincronización DB → Google Calendar.
    """
    print("=" * 70)
    print("PRUEBA DE SINCRONIZACIÓN DB → GOOGLE CALENDAR")
    print("=" * 70)
    print()

    async_session_maker = get_session_factory()

    async with async_session_maker() as session:
        booking_service = BookingService(session)

        # 1. Verificar que César tiene calendar_email
        from sqlalchemy import text
        result = await session.execute(
            text("SELECT id, first_name, last_name, calendar_email FROM doctors WHERE id = 1")
        )
        doctor = result.fetchone()

        if not doctor:
            print("❌ Doctor César no encontrado en la BD")
            return False

        print(f"👨‍⚕️ Doctor: {doctor[1]} {doctor[2]}")
        print(f"   ID: {doctor[0]}")
        print(f"   Calendar Email: {doctor[3] or '❌ NO CONFIGURADO'}")
        print()

        if not doctor[3]:
            print("⚠️  ADVERTENCIA: Doctor no tiene calendar_email configurado")
            print("   La sincronización no funcionará hasta que se configure.")
            print()
            print("   Para configurar, ejecuta:")
            print(f"   UPDATE doctors SET calendar_email = 'tu_email@gmail.com' WHERE id = 1;")
            print()
            return False

        # 2. Verificar que existe un paciente
        result = await session.execute(
            text("SELECT id, first_name, last_name, rut, phone FROM patients LIMIT 1")
        )
        patient = result.fetchone()

        if not patient:
            print("❌ No hay pacientes en la BD. Crea uno primero.")
            return False

        print(f"👤 Paciente de prueba: {patient[1]} {patient[2]}")
        print(f"   ID: {patient[0]}")
        print(f"   RUT: {patient[3]}")
        print(f"   Teléfono: {patient[4]}")
        print()

        # 3. Buscar slot disponible
        from src.services.availability_service import AvailabilityService
        from datetime import date

        availability_service = AvailabilityService(session)

        today = date.today()
        end_date = today + timedelta(days=7)

        print(f"🔍 Buscando slots disponibles (próximos 7 días)...")
        slots = await availability_service.get_available_slots(
            doctor_id=doctor[0],
            start_date=today,
            end_date=end_date
        )

        if not slots:
            print("❌ No hay slots disponibles para reservar")
            return False

        # Usar el primer slot disponible en el futuro
        now = datetime.now()
        future_slots = [s for s in slots if s.start_datetime > now]

        if not future_slots:
            print("❌ No hay slots futuros disponibles")
            return False

        selected_slot = future_slots[0]
        print(f"✅ Slot seleccionado:")
        print(f"   Fecha: {selected_slot.start_datetime.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Tipo: {selected_slot.appointment_type_name}")
        print(f"   Duración: {selected_slot.duration_minutes} min")
        print()

        # 4. Crear cita (con sincronización automática)
        print("📝 Creando cita y sincronizando con Google Calendar...")
        try:
            appointment = await booking_service.book_appointment(
                patient_id=patient[0],
                doctor_id=doctor[0],
                appointment_date=selected_slot.start_datetime,
                appointment_type_id=selected_slot.appointment_type_id,
                notes=f"Cita de prueba de sincronización - {datetime.now().isoformat()}"
            )

            await session.commit()

            print(f"✅ Cita creada exitosamente:")
            print(f"   ID: {appointment.id}")
            print(f"   Estado: {appointment.status.value}")
            print(f"   Google Calendar Event ID: {appointment.calendar_event_id or '❌ NO SINCRONIZADO'}")
            print()

            if appointment.calendar_event_id:
                print("🎉 ¡SINCRONIZACIÓN EXITOSA!")
                print(f"   Revisa tu Google Calendar: {doctor[3]}")
                print(f"   Deberías ver el evento: \"Cita: {patient[1]} {patient[2]}\"")
                print(f"   Fecha/hora: {selected_slot.start_datetime.strftime('%Y-%m-%d %H:%M')}")
                print(f"   Color: Lavanda (PENDING)")
                print()
            else:
                print("⚠️  Cita creada en DB pero NO sincronizada con Calendar")
                print("   Revisa los logs para ver el error.")
                print()

            # 5. Probar actualización de color (PENDING → CONFIRMED)
            print("🔄 Probando actualización de color (PENDING → CONFIRMED)...")
            confirmed_appointment = await booking_service.confirm_appointment(appointment.id)
            await session.commit()

            if confirmed_appointment.calendar_event_id:
                print("✅ Color actualizado en Calendar")
                print("   Revisa: El evento debería cambiar de lavanda → verde")
                print()
            else:
                print("⚠️  No se pudo actualizar color (sin calendar_event_id)")
                print()

            # 6. Probar cancelación
            input("\n⏸️  Presiona Enter para CANCELAR la cita y eliminar del calendar...")

            print("🗑️  Cancelando cita y eliminando de Google Calendar...")
            cancelled_appointment = await booking_service.cancel_appointment(
                appointment.id,
                cancel_reason="Prueba de sincronización completada"
            )
            await session.commit()

            print("✅ Cita cancelada en DB")
            print("   Revisa tu Calendar: El evento debería DESAPARECER")
            print()

        except Exception as e:
            print(f"❌ Error durante la prueba: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
            return False

        print("=" * 70)
        print("✅ PRUEBA COMPLETADA")
        print("=" * 70)

    return True


if __name__ == '__main__':
    try:
        success = asyncio.run(test_calendar_sync())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Prueba interrumpida por usuario")
        sys.exit(1)
