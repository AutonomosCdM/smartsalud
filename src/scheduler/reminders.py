"""
Daily reminder logic.

Finds pending appointments and sends WhatsApp reminders.
"""
from datetime import datetime, timedelta
import structlog

from src.core.config import settings
from src.database.connection import get_session
from src.database.models import Appointment, Patient
from src.whatsapp.service import TwilioService
from src.whatsapp.templates import reminder_message

logger = structlog.get_logger(__name__)


async def send_daily_reminders():
    """
    Send reminders for appointments happening tomorrow.

    Flow:
    1. Calculate target date (tomorrow)
    2. Query PENDING appointments for that date
    3. For each appointment:
       - Format reminder message
       - Send via WhatsApp
       - Log interaction
    4. Log summary
    """
    logger.info("starting_daily_reminders")

    # Calculate target date
    target_date = datetime.now() + timedelta(days=settings.reminder_days_ahead)
    target_date_start = target_date.replace(hour=0, minute=0, second=0)
    target_date_end = target_date.replace(hour=23, minute=59, second=59)

    # TODO: Implement in Phase 4
    # Query appointments
    # Send reminders
    # Log results

    logger.info(
        "daily_reminders_completed",
        target_date=target_date_start.isoformat(),
        reminders_sent=0  # Placeholder
    )
