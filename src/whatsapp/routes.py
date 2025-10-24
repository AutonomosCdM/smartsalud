"""
WhatsApp webhook endpoint.

Receives incoming messages from Twilio and processes them.
"""
from fastapi import APIRouter, Request, Depends, Form, Response
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from twilio.rest import Client

from src.api.dependencies import get_db
from src.nlp.service import NLPService
from src.nlp.intents import Intent
from src.whatsapp.handlers import (
    handle_confirm,
    handle_cancel,
    handle_unknown,
    handle_yes_reschedule,
    handle_no_reschedule,
    handle_timeslot_selection
)
from src.whatsapp.response_types import HandlerResponse, ResponseAction
from src.whatsapp.content_templates import ContentTemplateService
from src.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/webhook", tags=["whatsapp"])


@router.post("/whatsapp", response_class=PlainTextResponse)
async def whatsapp_webhook(
    From: str = Form(..., description="WhatsApp phone number of sender"),
    Body: str = Form(..., description="Message body text"),
    MessageSid: str = Form(None, description="Twilio Message SID"),
    ButtonPayload: str = Form(None, description="Button ID when quick reply button is tapped"),
    ButtonText: str = Form(None, description="Button text when quick reply button is tapped"),
    db: AsyncSession = Depends(get_db)
) -> str:
    """
    Twilio WhatsApp webhook endpoint.

    Receives messages from Twilio and responds via TwiML.

    Flow:
    1. Extract message details (phone, body)
    2. Detect intent via NLP
    3. Route to appropriate handler
    4. Respond with TwiML

    Args:
        From: Sender WhatsApp phone (e.g., whatsapp:+56912345678)
        Body: Message text
        MessageSid: Twilio Message SID for deduplication
        db: Database session

    Returns:
        TwiML XML response with message
    """
    logger.info(
        "webhook_received",
        from_number=From,
        message_preview=Body[:50] if Body else None,
        message_sid=MessageSid,
        button_payload=ButtonPayload,
        button_text=ButtonText
    )

    try:
        # CRITICAL: Check if this MessageSid was already processed (prevent button loop)
        if ButtonPayload and MessageSid:
            from src.database.repositories import InteractionRepository
            interaction_repo = InteractionRepository(db)
            existing_interaction = await interaction_repo.get_by_message_sid(MessageSid)

            if existing_interaction:
                logger.info(
                    "duplicate_message_ignored",
                    message_sid=MessageSid,
                    from_number=From,
                    button_payload=ButtonPayload
                )
                # Return early - button already processed
                client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
                message = client.messages.create(
                    from_=settings.twilio_whatsapp_number,
                    to=From,
                    body="Esta acción ya fue procesada anteriormente."
                )
                return Response(status_code=200)

        # Detect intent - prioritize button payload over NLP
        handler_response = None  # Will hold HandlerResponse from handlers

        if ButtonPayload:
            # User tapped an interactive button - route directly to handler
            if ButtonPayload == "CONFIRM":
                logger.info("button_confirm_pressed", from_number=From)
                response_message = await handle_confirm(
                    phone=From,
                    message=Body or ButtonText or "Confirmar",
                    db=db,
                    detected_intent="confirm",
                    confidence_score=100
                )
                # handle_confirm returns string, wrap in HandlerResponse
                handler_response = HandlerResponse.text(response_message)

            elif ButtonPayload == "CANCEL":
                logger.info("button_cancel_pressed", from_number=From)
                handler_response = await handle_cancel(
                    phone=From,
                    message=Body or ButtonText or "Cancelar",
                    db=db,
                    detected_intent="cancel",
                    confidence_score=100
                )
                # handle_cancel returns HandlerResponse directly

            elif ButtonPayload == "YES_RESCHEDULE":
                logger.info("button_yes_reschedule_pressed", from_number=From)
                handler_response = await handle_yes_reschedule(
                    phone=From,
                    message=Body or ButtonText or "Sí, reagendar",
                    db=db,
                    message_sid=MessageSid
                )

            elif ButtonPayload == "NO_RESCHEDULE":
                logger.info("button_no_reschedule_pressed", from_number=From)
                handler_response = await handle_no_reschedule(
                    phone=From,
                    message=Body or ButtonText or "No, gracias",
                    db=db,
                    message_sid=MessageSid
                )

            elif ButtonPayload == "SLOT_1":
                logger.info("button_slot1_pressed", from_number=From)
                handler_response = await handle_timeslot_selection(
                    phone=From,
                    message=Body or ButtonText or "Opción 1",
                    slot_number=1,
                    db=db,
                    message_sid=MessageSid
                )

            elif ButtonPayload == "SLOT_2":
                logger.info("button_slot2_pressed", from_number=From)
                handler_response = await handle_timeslot_selection(
                    phone=From,
                    message=Body or ButtonText or "Opción 2",
                    slot_number=2,
                    db=db,
                    message_sid=MessageSid
                )

            elif ButtonPayload == "SLOT_3":
                logger.info("button_slot3_pressed", from_number=From)
                handler_response = await handle_timeslot_selection(
                    phone=From,
                    message=Body or ButtonText or "Opción 3",
                    slot_number=3,
                    db=db,
                    message_sid=MessageSid
                )

            else:
                logger.warning("unknown_button_payload", from_number=From, button_payload=ButtonPayload)
                response_message = await handle_unknown(
                    phone=From,
                    message=Body or ButtonText or "Button pressed",
                    db=db,
                    detected_intent="unknown",
                    confidence_score=50
                )
                handler_response = HandlerResponse.text(response_message)

        else:
            # No button - use NLP to detect intent from text
            nlp_service = NLPService()
            intent_result = await nlp_service.detect_intent(Body)
            intent = intent_result.intent
            confidence = intent_result.confidence

            logger.info(
                "nlp_intent_detected",
                from_number=From,
                intent=intent.value,
                confidence=confidence
            )

            # Route to appropriate handler based on NLP intent
            if intent == Intent.CONFIRM:
                response_message = await handle_confirm(
                    phone=From,
                    message=Body,
                    db=db,
                    detected_intent=intent.value,
                    confidence_score=int(confidence * 100)
                )
                handler_response = HandlerResponse.text(response_message)

            elif intent == Intent.CANCEL:
                handler_response = await handle_cancel(
                    phone=From,
                    message=Body,
                    db=db,
                    detected_intent=intent.value,
                    confidence_score=int(confidence * 100)
                )

            else:
                response_message = await handle_unknown(
                    phone=From,
                    message=Body,
                    db=db,
                    detected_intent=intent.value,
                    confidence_score=int(confidence * 100)
                )
                handler_response = HandlerResponse.text(response_message)

        # Now process the HandlerResponse based on its action
        logger.info(
            "webhook_processed_successfully",
            from_number=From,
            action=handler_response.action.value
        )

        # Process HandlerResponse based on its action
        content_service = ContentTemplateService()

        # For button interactions, always use Messages API (not TwiML)
        if ButtonPayload:
            try:
                if handler_response.action == ResponseAction.SEND_TEXT:
                    # Simple text response
                    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
                    message = client.messages.create(
                        from_=settings.twilio_whatsapp_number,
                        to=From,
                        body=handler_response.message
                    )
                    logger.info("text_response_sent", message_sid=message.sid, from_number=From)

                elif handler_response.action == ResponseAction.SEND_RESCHEDULE_BUTTONS:
                    # Send reschedule prompt with buttons
                    patient_name = handler_response.data.get("patient_name")
                    message_sid = content_service.send_reschedule_prompt(
                        to=From,
                        patient_name=patient_name
                    )
                    logger.info("reschedule_prompt_sent", message_sid=message_sid, from_number=From)

                elif handler_response.action == ResponseAction.SEND_GOODBYE:
                    # Send goodbye message
                    patient_name = handler_response.data.get("patient_name")
                    message_sid = content_service.send_goodbye_message(
                        to=From,
                        patient_name=patient_name
                    )
                    logger.info("goodbye_message_sent", message_sid=message_sid, from_number=From)

                elif handler_response.action == ResponseAction.SEND_TIMESLOT_BUTTONS:
                    # Send timeslot options with buttons
                    patient_name = handler_response.data.get("patient_name")
                    slots = handler_response.data.get("slots", [])

                    message_sid = content_service.send_timeslot_options(
                        to=From,
                        patient_name=patient_name,
                        slots=slots
                    )
                    logger.info("timeslot_options_sent", message_sid=message_sid, from_number=From)

                # Return empty 200 OK response
                return Response(status_code=200)

            except Exception as send_error:
                logger.error(
                    "failed_to_send_button_response",
                    from_number=From,
                    error=str(send_error),
                    exc_info=True
                )
                # Still return 200 to acknowledge webhook
                return Response(status_code=200)
        else:
            # Regular text message from user (not button) - return TwiML response
            response_text = handler_response.message if handler_response.action == ResponseAction.SEND_TEXT else "Procesando..."
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response_text}</Message>
</Response>"""

            return twiml

    except Exception as e:
        logger.error(
            "webhook_processing_failed",
            from_number=From,
            error=str(e),
            exc_info=True
        )

        # Return generic error message
        error_message = """❌ Error al procesar tu mensaje

Ocurrió un error al procesar tu solicitud. Por favor intenta nuevamente o comunícate con el CESFAM.

CESFAM Futrono"""

        # For button interactions, send error via Messages API
        if ButtonPayload:
            try:
                client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
                client.messages.create(
                    from_=settings.twilio_whatsapp_number,
                    to=From,
                    body=error_message
                )
            except:
                pass  # Log already captured main error
            return Response(status_code=200)
        else:
            # Regular text message - return TwiML error
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{error_message}</Message>
</Response>"""

            return twiml


@router.get("/health")
async def webhook_health():
    """
    Health check endpoint for webhook.

    Returns:
        Status message
    """
    return {"status": "ok", "service": "whatsapp_webhook"}
