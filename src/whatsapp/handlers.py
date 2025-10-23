"""
Business logic handlers for WhatsApp intents.

Expected size: ~150 lines
"""
from sqlalchemy.ext.asyncio import AsyncSession


async def handle_confirm(phone: str, message: str, db: AsyncSession) -> str:
    """
    Handle CONFIRM intent.

    Flow:
    1. Get patient by phone
    2. Get pending appointment
    3. Update status to CONFIRMED
    4. Update Google Calendar color
    5. Log interaction
    6. Return confirmation message
    """
    # TODO: Implement in Phase 2
    pass


async def handle_cancel(phone: str, message: str, db: AsyncSession) -> str:
    """
    Handle CANCEL intent.

    Flow:
    1. Get patient by phone
    2. Get pending appointment
    3. Update status to CANCELLED
    4. Update Google Calendar color
    5. Log interaction
    6. Return cancellation message
    """
    # TODO: Implement in Phase 2
    pass


async def handle_unknown(phone: str, message: str, db: AsyncSession) -> str:
    """
    Handle UNKNOWN intent.

    Returns a friendly message asking for clarification.
    """
    # TODO: Implement in Phase 2
    pass
