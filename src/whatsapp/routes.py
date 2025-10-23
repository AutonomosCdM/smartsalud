"""
WhatsApp webhook endpoint.

Receives incoming messages from Twilio and processes them.
"""
from fastapi import APIRouter, Request, Depends, Form, Response
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.api.dependencies import get_db
from src.nlp.service import NLPService
from src.nlp.intents import Intent
from src.whatsapp.handlers import handle_confirm, handle_cancel, handle_unknown

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/webhook", tags=["whatsapp"])


@router.post("/whatsapp", response_class=PlainTextResponse)
async def whatsapp_webhook(
    From: str = Form(..., description="WhatsApp phone number of sender"),
    Body: str = Form(..., description="Message body text"),
    MessageSid: str = Form(None, description="Twilio Message SID"),
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
        message_sid=MessageSid
    )

    try:
        # Initialize NLP service
        nlp_service = NLPService()

        # Detect intent
        intent_result = await nlp_service.detect_intent(Body)

        logger.info(
            "intent_detected",
            from_number=From,
            intent=intent_result.intent.value,
            confidence=intent_result.confidence
        )

        # Route to appropriate handler
        if intent_result.intent == Intent.CONFIRM:
            response_message = await handle_confirm(
                phone=From,
                message=Body,
                db=db,
                detected_intent=intent_result.intent.value,
                confidence_score=int(intent_result.confidence * 100)
            )
        elif intent_result.intent == Intent.CANCEL:
            response_message = await handle_cancel(
                phone=From,
                message=Body,
                db=db,
                detected_intent=intent_result.intent.value,
                confidence_score=int(intent_result.confidence * 100)
            )
        else:
            response_message = await handle_unknown(
                phone=From,
                message=Body,
                db=db,
                detected_intent=intent_result.intent.value,
                confidence_score=int(intent_result.confidence * 100)
            )

        logger.info(
            "webhook_processed_successfully",
            from_number=From,
            intent=intent_result.intent.value
        )

        # Return TwiML response
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response_message}</Message>
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
