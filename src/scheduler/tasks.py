"""
APScheduler task configuration.

Schedules daily reminder task.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import structlog

from src.core.config import get_settings
from src.scheduler.reminders import send_daily_reminders

logger = structlog.get_logger(__name__)


def setup_scheduler() -> AsyncIOScheduler:
    """
    Setup and configure APScheduler.

    Schedule:
    - Daily reminders at configured time (default: 9:00 AM)

    Returns:
        Configured scheduler instance
    """
    scheduler = AsyncIOScheduler()

    # Schedule daily reminders
    scheduler.add_job(
        send_daily_reminders,
        trigger=CronTrigger(
            hour=settings.reminder_schedule_hour,
            minute=settings.reminder_schedule_minute
        ),
        id="daily_reminders",
        name="Send daily appointment reminders",
        replace_existing=True
    )

    logger.info(
        "scheduler_configured",
        reminder_time=f"{settings.reminder_schedule_hour:02d}:{settings.reminder_schedule_minute:02d}"
    )

    return scheduler
