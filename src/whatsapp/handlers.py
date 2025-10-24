"""
Business logic handlers for WhatsApp intents.

Implements CONFIRM/CANCEL/UNKNOWN intent handling with database operations.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.database.repositories import (
    PatientRepository,
    AppointmentRepository,
    InteractionRepository
)
from src.database.models import AppointmentStatus
from src.whatsapp.templates import (
    confirmation_message,
    cancellation_message,
    unknown_intent_message,
    no_appointment_message,
    patient_not_found_message
)
from src.whatsapp.response_types import HandlerResponse, ResponseAction
from src.calendar.service import CalendarService

logger = structlog.get_logger(__name__)


async def handle_confirm(
    phone: str,
    message: str,
    db: AsyncSession,
    detected_intent: str = "confirm",
    confidence_score: int = 100
) -> str:
    """
    Handle CONFIRM intent.

    Flow:
    1. Get patient by phone
    2. Get pending appointment
    3. Update status to CONFIRMED
    4. Update Google Calendar color
    5. Log interaction
    6. Return confirmation message

    Args:
        phone: WhatsApp phone number (format: whatsapp:+56XXXXXXXXX)
        message: Original message text
        db: Database session
        detected_intent: Intent string from NLP
        confidence_score: Confidence score from NLP (0-100)

    Returns:
        Response message to send back
    """
    patient_repo = PatientRepository(db)
    appointment_repo = AppointmentRepository(db)
    interaction_repo = InteractionRepository(db)

    # Get patient
    patient = await patient_repo.get_by_phone(phone)
    if not patient:
        logger.warning("patient_not_found", phone=phone)
        return patient_not_found_message()

    # Get pending appointment
    appointment = await appointment_repo.get_pending_for_patient(patient.id)
    if not appointment:
        logger.info("no_pending_appointment", patient_id=patient.id)

        # Log interaction without appointment
        await interaction_repo.create(
            patient_id=patient.id,
            message_from=phone,
            message_to="system",
            message_body=message,
            detected_intent=detected_intent,
            confidence_score=confidence_score
        )
        await db.commit()

        return no_appointment_message()

    # Confirm appointment
    success = await appointment_repo.confirm_appointment(appointment.id)
    if not success:
        logger.error("failed_to_confirm", appointment_id=appointment.id)
        return unknown_intent_message()

    # Update Google Calendar color (Phase 3 - currently just logs)
    if appointment.calendar_event_id:
        calendar_service = CalendarService()
        try:
            await calendar_service.update_event_color(
                appointment.calendar_event_id,
                "CONFIRMED"
            )
        except Exception as e:
            logger.warning(
                "calendar_update_failed",
                appointment_id=appointment.id,
                error=str(e)
            )

    # Log interaction
    await interaction_repo.create(
        patient_id=patient.id,
        appointment_id=appointment.id,
        message_from=phone,
        message_to="system",
        message_body=message,
        detected_intent=detected_intent,
        confidence_score=confidence_score
    )

    # Commit all changes
    await db.commit()

    logger.info(
        "appointment_confirmed_successfully",
        appointment_id=appointment.id,
        patient_id=patient.id
    )

    # Return formatted confirmation message
    return confirmation_message(
        patient_name=patient.first_name,
        appointment_date=appointment.appointment_date.strftime("%d/%m/%Y %H:%M"),
        doctor_name=appointment.doctor_name
    )


async def handle_cancel(
    phone: str,
    message: str,
    db: AsyncSession,
    detected_intent: str = "cancel",
    confidence_score: int = 100
) -> HandlerResponse:
    """
    Handle CANCEL intent.

    Flow:
    1. Get patient by phone
    2. Get pending appointment
    3. Update status to CANCELLED
    4. Update Google Calendar color
    5. Log interaction
    6. Ask if user wants to reschedule

    Args:
        phone: WhatsApp phone number (format: whatsapp:+56XXXXXXXXX)
        message: Original message text
        db: Database session
        detected_intent: Intent string from NLP
        confidence_score: Confidence score from NLP (0-100)

    Returns:
        HandlerResponse with action to ask for reschedule
    """
    patient_repo = PatientRepository(db)
    appointment_repo = AppointmentRepository(db)
    interaction_repo = InteractionRepository(db)

    # Get patient
    patient = await patient_repo.get_by_phone(phone)
    if not patient:
        logger.warning("patient_not_found", phone=phone)
        return HandlerResponse.text(patient_not_found_message())

    # Get pending appointment
    appointment = await appointment_repo.get_pending_for_patient(patient.id)
    if not appointment:
        logger.info("no_pending_appointment", patient_id=patient.id)

        # Log interaction without appointment
        await interaction_repo.create(
            patient_id=patient.id,
            message_from=phone,
            message_to="system",
            message_body=message,
            detected_intent=detected_intent,
            confidence_score=confidence_score
        )
        await db.commit()

        return HandlerResponse.text(no_appointment_message())

    # Cancel appointment
    success = await appointment_repo.cancel_appointment(appointment.id)
    if not success:
        logger.error("failed_to_cancel", appointment_id=appointment.id)
        return HandlerResponse.text(unknown_intent_message())

    # Update Google Calendar color (Phase 3 - currently just logs)
    if appointment.calendar_event_id:
        calendar_service = CalendarService()
        try:
            await calendar_service.update_event_color(
                appointment.calendar_event_id,
                "CANCELLED"
            )
        except Exception as e:
            logger.warning(
                "calendar_update_failed",
                appointment_id=appointment.id,
                error=str(e)
            )

    # Log interaction
    await interaction_repo.create(
        patient_id=patient.id,
        appointment_id=appointment.id,
        message_from=phone,
        message_to="system",
        message_body=message,
        detected_intent=detected_intent,
        confidence_score=confidence_score
    )

    # Commit all changes
    await db.commit()

    logger.info(
        "appointment_cancelled_successfully",
        appointment_id=appointment.id,
        patient_id=patient.id
    )

    # Ask if user wants to reschedule (send buttons)
    return HandlerResponse.reschedule_prompt(
        patient_name=patient.first_name,
        phone=phone
    )


async def handle_yes_reschedule(
    phone: str,
    message: str,
    db: AsyncSession,
    message_sid: Optional[str] = None
) -> HandlerResponse:
    """
    Handle YES_RESCHEDULE button press.

    Validates that user has a recently cancelled appointment before
    showing reschedule options. Logs interaction to prevent duplicate processing.

    Args:
        phone: WhatsApp phone number
        message: Original message text
        db: Database session
        message_sid: Twilio MessageSid for deduplication

    Returns:
        HandlerResponse with timeslot options or validation error
    """
    patient_repo = PatientRepository(db)
    appointment_repo = AppointmentRepository(db)
    interaction_repo = InteractionRepository(db)

    patient = await patient_repo.get_by_phone(phone)
    if not patient:
        logger.warning("patient_not_found_reschedule", phone=phone)
        return HandlerResponse.text(patient_not_found_message())

    # CRITICAL: Verify user has recently cancelled appointment
    # This prevents loop when user presses old buttons
    cancelled_appt = await appointment_repo.get_recently_cancelled_for_patient(
        patient.id,
        hours=24  # Look back 24 hours
    )

    if not cancelled_appt:
        # No recent cancellation - button is from old message
        logger.info(
            "reschedule_button_no_recent_cancellation",
            patient_id=patient.id,
            phone=phone
        )
        return HandlerResponse.text(
            "Esta acción ya fue procesada. Si necesitas reagendar, contáctanos."
        )

    # Log interaction with MessageSid to prevent duplicate processing
    await interaction_repo.create(
        patient_id=patient.id,
        appointment_id=cancelled_appt.id,
        message_from=phone,
        message_to="system",
        message_body=message,
        detected_intent="yes_reschedule",
        confidence_score=100,
        twilio_message_sid=message_sid
    )
    await db.commit()

    logger.info(
        "reschedule_accepted",
        patient_id=patient.id,
        phone=phone,
        message_sid=message_sid
    )

    # Generate 3 available time slots
    # TODO: In the future, fetch these from an availability system
    from datetime import datetime, timedelta

    # Generate slots for different days and times
    tomorrow = datetime.now() + timedelta(days=1)
    day_after = datetime.now() + timedelta(days=2)
    three_days = datetime.now() + timedelta(days=3)

    # Slot 1: Tomorrow at 10:00
    slot1_date = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    slot1_id = f"SLOT_{slot1_date.strftime('%Y%m%d_%H%M')}"
    slot1_display = slot1_date.strftime("%d/%m/%Y a las %H:%M")

    # Slot 2: Day after tomorrow at 15:00
    slot2_date = day_after.replace(hour=15, minute=0, second=0, microsecond=0)
    slot2_id = f"SLOT_{slot2_date.strftime('%Y%m%d_%H%M')}"
    slot2_display = slot2_date.strftime("%d/%m/%Y a las %H:%M")

    # Slot 3: Three days from now at 11:30
    slot3_date = three_days.replace(hour=11, minute=30, second=0, microsecond=0)
    slot3_id = f"SLOT_{slot3_date.strftime('%Y%m%d_%H%M')}"
    slot3_display = slot3_date.strftime("%d/%m/%Y a las %H:%M")

    slots = [
        {"id": slot1_id, "display": slot1_display, "datetime": slot1_date},
        {"id": slot2_id, "display": slot2_display, "datetime": slot2_date},
        {"id": slot3_id, "display": slot3_display, "datetime": slot3_date}
    ]

    logger.info(
        "timeslots_generated",
        patient_id=patient.id,
        slot1=slot1_display,
        slot2=slot2_display,
        slot3=slot3_display
    )

    return HandlerResponse.timeslot_options(
        patient_name=patient.first_name,
        phone=phone,
        slots=slots
    )


async def handle_timeslot_selection(
    phone: str,
    message: str,
    slot_number: int,
    db: AsyncSession,
    message_sid: Optional[str] = None
) -> HandlerResponse:
    """
    Handle timeslot selection (SLOT_1 or SLOT_2).

    Creates a new appointment with the selected timeslot.

    Args:
        phone: WhatsApp phone number
        message: Original message text
        slot_number: 1 or 2 indicating which slot was selected
        db: Database session
        message_sid: Twilio MessageSid for deduplication

    Returns:
        HandlerResponse with confirmation message
    """
    from datetime import datetime, timedelta

    patient_repo = PatientRepository(db)
    appointment_repo = AppointmentRepository(db)
    interaction_repo = InteractionRepository(db)

    patient = await patient_repo.get_by_phone(phone)
    if not patient:
        logger.warning("patient_not_found_timeslot", phone=phone)
        return HandlerResponse.text(patient_not_found_message())

    # Verify user has recently cancelled appointment
    cancelled_appt = await appointment_repo.get_recently_cancelled_for_patient(
        patient.id,
        hours=24
    )

    if not cancelled_appt:
        logger.info(
            "timeslot_selection_no_recent_cancellation",
            patient_id=patient.id,
            phone=phone
        )
        return HandlerResponse.text(
            "Esta acción ya fue procesada. Si necesitas reagendar, contáctanos."
        )

    # Log interaction to prevent duplicate processing
    await interaction_repo.create(
        patient_id=patient.id,
        appointment_id=cancelled_appt.id,
        message_from=phone,
        message_to="system",
        message_body=message,
        detected_intent=f"timeslot_slot_{slot_number}",
        confidence_score=100,
        twilio_message_sid=message_sid
    )
    await db.commit()

    # Regenerate slots using same logic as handle_yes_reschedule
    tomorrow = datetime.now() + timedelta(days=1)
    day_after = datetime.now() + timedelta(days=2)
    three_days = datetime.now() + timedelta(days=3)

    # Slot 1: Tomorrow at 10:00
    slot1_date = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    # Slot 2: Day after tomorrow at 15:00
    slot2_date = day_after.replace(hour=15, minute=0, second=0, microsecond=0)
    # Slot 3: Three days from now at 11:30
    slot3_date = three_days.replace(hour=11, minute=30, second=0, microsecond=0)

    # Select the chosen slot
    if slot_number == 1:
        selected_date = slot1_date
    elif slot_number == 2:
        selected_date = slot2_date
    else:  # slot_number == 3
        selected_date = slot3_date

    selected_display = selected_date.strftime("%d/%m/%Y a las %H:%M")

    # Create new appointment with selected timeslot
    new_appointment = await appointment_repo.create(
        patient_id=patient.id,
        appointment_date=selected_date,
        doctor_name=cancelled_appt.doctor_name,
        specialty=cancelled_appt.specialty,
        status=AppointmentStatus.PENDING
    )
    await db.commit()

    # Create event in Google Calendar
    calendar_service = CalendarService()
    if calendar_service.service:  # Only if calendar is configured
        end_time = selected_date + timedelta(minutes=30)

        event_id = await calendar_service.create_event(
            summary=f"Cita - {patient.first_name} {patient.last_name}",
            start_time=selected_date,
            end_time=end_time,
            description=f"📋 Paciente: {patient.first_name} {patient.last_name}\n"
                       f"👨‍⚕️ Doctor: {new_appointment.doctor_name}\n"
                       f"🏥 Especialidad: {new_appointment.specialty}\n"
                       f"📞 Teléfono: {patient.phone}",
            status="PENDING"
        )

        # Save event_id in appointment
        if event_id:
            new_appointment.calendar_event_id = event_id
            await db.commit()
            logger.info(
                "calendar_event_created_for_appointment",
                appointment_id=new_appointment.id,
                event_id=event_id
            )

    logger.info(
        "appointment_rescheduled",
        patient_id=patient.id,
        old_appointment_id=cancelled_appt.id,
        new_appointment_id=new_appointment.id,
        new_date=selected_display,
        slot_number=slot_number
    )

    confirmation_message = f"""✅ ¡Cita reagendada exitosamente, {patient.first_name}!

📅 Nueva fecha: {selected_display}
👨‍⚕️ Doctor: {new_appointment.doctor_name}
🏥 Especialidad: {new_appointment.specialty}

Te enviaremos un recordatorio antes de tu cita.

CESFAM Futrono"""

    return HandlerResponse.text(confirmation_message)


async def handle_no_reschedule(
    phone: str,
    message: str,
    db: AsyncSession,
    message_sid: Optional[str] = None
) -> HandlerResponse:
    """
    Handle NO_RESCHEDULE button press.

    Validates that user has recently cancelled appointment before
    sending goodbye message. Logs interaction to prevent duplicate processing.

    Args:
        phone: WhatsApp phone number
        message: Original message text
        db: Database session
        message_sid: Twilio MessageSid for deduplication

    Returns:
        HandlerResponse with goodbye message or validation error
    """
    patient_repo = PatientRepository(db)
    appointment_repo = AppointmentRepository(db)
    interaction_repo = InteractionRepository(db)

    patient = await patient_repo.get_by_phone(phone)
    if not patient:
        logger.warning("patient_not_found_goodbye", phone=phone)
        return HandlerResponse.text("¡Gracias! Si necesitas algo, contáctanos.")

    # CRITICAL: Verify user has recently cancelled appointment
    # This prevents loop when user presses old buttons
    cancelled_appt = await appointment_repo.get_recently_cancelled_for_patient(
        patient.id,
        hours=24  # Look back 24 hours
    )

    if not cancelled_appt:
        # No recent cancellation - button is from old message
        logger.info(
            "no_reschedule_button_no_recent_cancellation",
            patient_id=patient.id,
            phone=phone
        )
        return HandlerResponse.text(
            "Esta acción ya fue procesada. Si necesitas algo más, contáctanos."
        )

    # Log interaction with MessageSid to prevent duplicate processing
    await interaction_repo.create(
        patient_id=patient.id,
        appointment_id=cancelled_appt.id,
        message_from=phone,
        message_to="system",
        message_body=message,
        detected_intent="no_reschedule",
        confidence_score=100,
        twilio_message_sid=message_sid
    )
    await db.commit()

    logger.info(
        "reschedule_declined",
        patient_id=patient.id,
        message_sid=message_sid,
        phone=phone
    )

    return HandlerResponse.goodbye(patient_name=patient.first_name)


async def handle_unknown(
    phone: str,
    message: str,
    db: AsyncSession,
    detected_intent: str = "unknown",
    confidence_score: int = 0
) -> str:
    """
    Handle UNKNOWN intent.

    Returns a friendly message asking for clarification.
    Logs the interaction for future analysis.

    Args:
        phone: WhatsApp phone number (format: whatsapp:+56XXXXXXXXX)
        message: Original message text
        db: Database session
        detected_intent: Intent string from NLP
        confidence_score: Confidence score from NLP (0-100)

    Returns:
        Response message asking for clarification
    """
    patient_repo = PatientRepository(db)
    interaction_repo = InteractionRepository(db)

    # Try to get patient (may not exist yet)
    patient = await patient_repo.get_by_phone(phone)

    if patient:
        # Log interaction
        await interaction_repo.create(
            patient_id=patient.id,
            message_from=phone,
            message_to="system",
            message_body=message,
            detected_intent=detected_intent,
            confidence_score=confidence_score
        )
        await db.commit()

    logger.info(
        "unknown_intent_received",
        phone=phone,
        patient_id=patient.id if patient else None,
        message_preview=message[:50]
    )

    return unknown_intent_message()
