"""
Simple monitoring dashboard endpoint.

Shows basic metrics about system usage.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.api.dependencies import get_db
from src.database.models import Interaction, Appointment
from src.core.config import settings

router = APIRouter(tags=["monitoring"])


@router.get("/dashboard")
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    """
    Get dashboard metrics.

    Returns:
    - Total messages today
    - Confirmation rate
    - Groq vs Regex usage
    - Error rate
    """
    if not settings.enable_dashboard:
        return {"error": "Dashboard disabled"}

    today = datetime.now().replace(hour=0, minute=0, second=0)

    # TODO: Implement in Phase 5
    # Query metrics from database

    return {
        "status": "healthy",
        "date": today.isoformat(),
        "metrics": {
            "messages_today": 0,
            "confirmation_rate": 0.0,
            "nlp_groq_percentage": 0.0,
            "nlp_regex_percentage": 0.0,
            "error_rate": 0.0
        },
        "message": "Dashboard metrics - TODO: Implement in Phase 5"
    }
