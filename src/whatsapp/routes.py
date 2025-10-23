"""
WhatsApp webhook endpoint.

Receives incoming messages from Twilio and processes them.
Expected size: ~100 lines
"""
from fastapi import APIRouter, Request, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db

router = APIRouter(prefix="/api/webhook", tags=["whatsapp"])


@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Twilio WhatsApp webhook endpoint.

    Receives messages and responds via TwiML.

    Flow:
    1. Extract message details (phone, body)
    2. Detect intent via NLP
    3. Route to appropriate handler
    4. Respond with TwiML
    """
    # TODO: Implement in Phase 2
    pass
