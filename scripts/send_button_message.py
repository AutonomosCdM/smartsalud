"""
Send WhatsApp message with interactive buttons using existing Content Template.
"""
import asyncio
from datetime import datetime
from src.whatsapp.content_templates import ContentTemplateService
from src.database.connection import get_session_factory
from src.database.repositories import PatientRepository, AppointmentRepository


# Use the ContentSid that was created
CONTENT_SID = "HXc5b986feaeba8f5312259fd918fad3c6"


async def send_button_message():
    """Send WhatsApp message with buttons to Cesar."""
    print("="*60)
    print("SENDING WHATSAPP MESSAGE WITH INTERACTIVE BUTTONS")
    print("="*60)

    content_service = ContentTemplateService()
    session_factory = get_session_factory()

    async with session_factory() as session:
        patient_repo = PatientRepository(session)
        appointment_repo = AppointmentRepository(session)

        # Get Cesar's info
        cesar_phone = "whatsapp:+56978754779"
        patient = await patient_repo.get_by_phone(cesar_phone)

        if not patient:
            print(f"❌ Patient not found: {cesar_phone}")
            return

        print(f"\n✓ Patient: {patient.first_name} {patient.last_name}")
        print(f"  Phone: {patient.phone}")

        # Get pending appointment
        appointment = await appointment_repo.get_pending_for_patient(patient.id)

        if not appointment:
            print(f"❌ No pending appointment for patient {patient.id}")
            return

        print(f"\n✓ Pending appointment:")
        print(f"  Date: {appointment.appointment_date}")
        print(f"  Doctor: {appointment.doctor_name}")
        print(f"  Specialty: {appointment.specialty}")

    # Format date
    appointment_date_str = appointment.appointment_date.strftime("%d de %B %Y, %H:%M")

    # Send message
    print(f"\n📤 Sending message with buttons...")
    print(f"  ContentSid: {CONTENT_SID}")

    try:
        message_sid = content_service.send_message_with_buttons(
            to=patient.phone,
            content_sid=CONTENT_SID,
            patient_name=patient.first_name,
            appointment_date=appointment_date_str,
            doctor_name=appointment.doctor_name,
            specialty=appointment.specialty or "Medicina General"
        )

        print(f"\n✅ Message sent successfully!")
        print(f"  MessageSid: {message_sid}")

        print("\n" + "="*60)
        print("CHECK WHATSAPP NOW!")
        print("="*60)
        print(f"\n📱 Check WhatsApp on {patient.phone}")
        print("\nYou should see 2 interactive buttons:")
        print("  [✅ Confirmar]  [❌ Cancelar]")
        print("\nTap a button to test the webhook!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Failed to send message: {e}")


if __name__ == "__main__":
    asyncio.run(send_button_message())
