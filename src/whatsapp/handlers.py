"""
Business logic handlers for WhatsApp intents.

Implements CONFIRM/CANCEL/UNKNOWN intent handling with database operations.
"""
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.database.repositories import (
    PatientRepository,
    AppointmentRepository,
    InteractionRepository
)
from src.whatsapp.templates import (
    confirmation_message,
    cancellation_message,
    unknown_intent_message,
    no_appointment_message,
    patient_not_found_message
)
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
) -> str:
    """
    Handle CANCEL intent.

    Flow:
    1. Get patient by phone
    2. Get pending appointment
    3. Update status to CANCELLED
    4. Update Google Calendar color
    5. Log interaction
    6. Return cancellation message

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

    # Cancel appointment
    success = await appointment_repo.cancel_appointment(appointment.id)
    if not success:
        logger.error("failed_to_cancel", appointment_id=appointment.id)
        return unknown_intent_message()

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

    # Return formatted cancellation message
    return cancellation_message(
        patient_name=patient.first_name,
        appointment_date=appointment.appointment_date.strftime("%d/%m/%Y %H:%M"),
        doctor_name=appointment.doctor_name
    )


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
