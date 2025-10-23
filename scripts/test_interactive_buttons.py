"""
Test script for interactive WhatsApp buttons.

Creates Content Template and sends message with buttons to test patient.
"""
import asyncio
from datetime import datetime
from src.whatsapp.content_templates import ContentTemplateService
from src.database.connection import get_session_factory
from src.database.repositories import PatientRepository, AppointmentRepository
import structlog

logger = structlog.get_logger(__name__)


async def test_interactive_buttons():
    """Test sending WhatsApp message with interactive buttons."""
    print("="*60)
    print("TESTING INTERACTIVE WHATSAPP BUTTONS")
    print("="*60)

    # Initialize services
    content_service = ContentTemplateService()
    session_factory = get_session_factory()

    async with session_factory() as session:
        patient_repo = PatientRepository(session)
        appointment_repo = AppointmentRepository(session)

        # Get Cesar's patient info
        cesar_phone = "whatsapp:+56978754779"
        patient = await patient_repo.get_by_phone(cesar_phone)

        if not patient:
            print(f"❌ Patient not found: {cesar_phone}")
            return

        print(f"\n✓ Found patient: {patient.first_name} {patient.last_name}")
        print(f"  Phone: {patient.phone}")

        # Get pending appointment
        appointment = await appointment_repo.get_pending_for_patient(patient.id)

        if not appointment:
            print(f"❌ No pending appointment found for patient {patient.id}")
            return

        print(f"\n✓ Found pending appointment:")
        print(f"  ID: {appointment.id}")
        print(f"  Date: {appointment.appointment_date}")
        print(f"  Doctor: {appointment.doctor_name}")
        print(f"  Specialty: {appointment.specialty}")

    # Step 1: Create Content Template
    print("\n" + "="*60)
    print("STEP 1: Creating Content Template with Buttons")
    print("="*60)

    try:
        content_sid = content_service.create_appointment_reminder_template()
        print(f"\n✓ Content Template created successfully!")
        print(f"  ContentSid: {content_sid}")
    except Exception as e:
        print(f"\n❌ Failed to create template: {e}")
        print("\nNote: If template already exists, you can list templates with:")
        print("  content_service.list_templates()")
        return

    # Step 2: Send message with buttons
    print("\n" + "="*60)
    print("STEP 2: Sending Message with Interactive Buttons")
    print("="*60)

    # Format appointment date
    appointment_date_str = appointment.appointment_date.strftime("%d de %B %Y, %H:%M")

    try:
        message_sid = content_service.send_message_with_buttons(
            to=patient.phone,
            content_sid=content_sid,
            patient_name=patient.first_name,
            appointment_date=appointment_date_str,
            doctor_name=appointment.doctor_name,
            specialty=appointment.specialty or "Medicina General"
        )

        print(f"\n✓ Message sent successfully!")
        print(f"  MessageSid: {message_sid}")
        print(f"  To: {patient.phone}")

    except Exception as e:
        print(f"\n❌ Failed to send message: {e}")
        return

    # Instructions
    print("\n" + "="*60)
    print("TESTING INSTRUCTIONS")
    print("="*60)
    print("\n📱 Check WhatsApp on +56978754779")
    print("\nYou should see a message with 2 buttons:")
    print("  [✅ Confirmar]  [❌ Cancelar]")
    print("\nTap a button to test:")
    print("  • Tapping ✅ Confirmar → Should confirm the appointment")
    print("  • Tapping ❌ Cancelar → Should cancel the appointment")
    print("\nWebhook will receive:")
    print("  • ButtonPayload: CONFIRM or CANCEL")
    print("  • ButtonText: ✅ Confirmar or ❌ Cancelar")
    print("\n" + "="*60)


async def list_existing_templates():
    """List existing Content Templates."""
    print("="*60)
    print("EXISTING CONTENT TEMPLATES")
    print("="*60)

    content_service = ContentTemplateService()

    try:
        templates = content_service.list_templates()

        if not templates:
            print("\nNo templates found.")
            return

        print(f"\nFound {len(templates)} template(s):\n")

        for t in templates:
            print(f"  • {t['friendly_name']}")
            print(f"    SID: {t['sid']}")
            print(f"    Language: {t['language']}")
            print(f"    Created: {t['date_created']}")
            print()

    except Exception as e:
        print(f"\n❌ Failed to list templates: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "list":
        asyncio.run(list_existing_templates())
    else:
        asyncio.run(test_interactive_buttons())
