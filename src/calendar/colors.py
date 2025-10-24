"""
Google Calendar color mapping.

Maps appointment status to calendar event colors.
"""
from enum import Enum


class CalendarColor(str, Enum):
    """Google Calendar color IDs."""

    # Google Calendar predefined colors
    LAVENDER = "1"
    SAGE = "2"
    GRAPE = "3"
    FLAMINGO = "4"
    BANANA = "5"
    TANGERINE = "6"
    PEACOCK = "7"
    GRAPHITE = "8"
    BLUEBERRY = "9"
    BASIL = "10"
    TOMATO = "11"


# Status to color mapping - Colores pasteles suaves
STATUS_COLOR_MAP = {
    "PENDING": CalendarColor.LAVENDER,    # Lavanda suave - awaiting response
    "CONFIRMED": CalendarColor.SAGE,      # Verde salvia suave - confirmed
    "CANCELLED": CalendarColor.FLAMINGO,  # Rosa coral suave - cancelled
    "COMPLETED": CalendarColor.PEACOCK,   # Azul turquesa suave - past appointment
    "NO_SHOW": CalendarColor.GRAPE,       # Morado pastel - didn't attend
}


def get_color_for_status(status: str) -> str:
    """
    Get Google Calendar color ID for appointment status.

    Args:
        status: Appointment status (PENDING, CONFIRMED, etc.)

    Returns:
        Google Calendar color ID
    """
    return STATUS_COLOR_MAP.get(status, CalendarColor.LAVENDER)
