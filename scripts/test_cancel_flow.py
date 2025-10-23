"""
Script to test cancel flow with reschedule buttons.
Creates a new appointment for Cesar and sends button message.
"""
import asyncio
from datetime import datetime, timedelta

from src.database.connection import get_session_factory
from src.database.repositories import PatientRepository, AppointmentRepository
from src.database.models import Appointment, AppointmentStatus
from src.whatsapp.content_templates import ContentTemplateService


async def main():
    """Create appointment and send button message to test cancel flow."""
    print("="*70)
    print("TESTING CANCEL FLOW WITH RESCHEDULE BUTTONS")
    print("="*70)

    session_factory = get_session_factory()
    content_service = ContentTemplateService()

    async with session_factory() as session:
        patient_repo = PatientRepository(session)
        appointment_repo = AppointmentRepository(session)

        # Get Cesar
        cesar_phone = "whatsapp:+56978754779"
        cesar = await patient_repo.get_by_phone(cesar_phone)

        if not cesar:
            print(f"❌ Cesar no encontrado en {cesar_phone}")
            return

        print(f"\n✅ Paciente encontrado: {cesar.first_name} {cesar.last_name} (ID: {cesar.id})")

        # Create new PENDING appointment
        tomorrow = datetime.now() + timedelta(days=1)
        appt_date = tomorrow.replace(hour=15, minute=30, second=0, microsecond=0)

        new_appt = Appointment(
            patient_id=cesar.id,
            appointment_date=appt_date,
            doctor_name="Dra. María González",
            specialty="Medicina General",
            status=AppointmentStatus.PENDING
        )
        session.add(new_appt)
        await session.commit()
        await session.refresh(new_appt)

        print(f"\n✅ Cita creada:")
        print(f"   ID: {new_appt.id}")
        print(f"   Fecha: {new_appt.appointment_date.strftime('%d/%m/%Y %H:%M')}")
        print(f"   Doctor: {new_appt.doctor_name}")
        print(f"   Status: {new_appt.status}")

    # Format date for message
    appointment_date_str = appt_date.strftime("%d de %B %Y, %H:%M")

    print(f"\n📱 Enviando mensaje con botones a {cesar.phone}...")

    try:
        # Get or create content template
        content_sid = content_service.get_or_create_reminder_template()

        message_sid = content_service.send_message_with_buttons(
            to=cesar.phone,
            content_sid=content_sid,
            patient_name=cesar.first_name,
            appointment_date=appointment_date_str,
            doctor_name=new_appt.doctor_name,
            specialty=new_appt.specialty
        )

        print(f"\n✅ Mensaje enviado!")
        print(f"   MessageSid: {message_sid}")
        print(f"\n" + "="*70)
        print("🎯 PRUEBA EL FLUJO DE CANCELACIÓN")
        print("="*70)
        print(f"\n1️⃣  Presiona el botón [❌ Cancelar] en WhatsApp")
        print(f"2️⃣  La cita se cancelará")
        print(f"3️⃣  Recibirás mensaje: '¿Deseas reagendar tu cita?'")
        print(f"4️⃣  Verás 2 botones:")
        print(f"     [✅ Sí, reagendar]")
        print(f"     [❌ No, gracias]")
        print(f"\n5️⃣  Prueba ambos botones para ver los mensajes!")
        print("="*70)

    except Exception as e:
        print(f"\n❌ Error enviando mensaje: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
