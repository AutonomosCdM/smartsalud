"""
Custom exceptions for smartSalud_V2.

All exceptions include context for structured logging.
"""
from typing import Dict, Any, Optional


class SmartSaludException(Exception):
    """Base exception for all smartSalud errors."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        self.message = message
        self.context = context or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dict for logging."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "context": self.context
        }


# Database Exceptions
class DatabaseError(SmartSaludException):
    """Database operation failed."""
    pass


class PatientNotFoundError(DatabaseError):
    """Patient not found in database."""
    pass


class AppointmentNotFoundError(DatabaseError):
    """Appointment not found in database."""
    pass


# NLP Exceptions
class NLPError(SmartSaludException):
    """NLP service error."""
    pass


class GroqAPIError(NLPError):
    """Groq API call failed."""
    pass


class IntentDetectionError(NLPError):
    """Intent detection failed."""
    pass


# WhatsApp Exceptions
class WhatsAppError(SmartSaludException):
    """WhatsApp service error."""
    pass


class TwilioAPIError(WhatsAppError):
    """Twilio API call failed."""
    pass


class MessageSendError(WhatsAppError):
    """Failed to send WhatsApp message."""
    pass


# Calendar Exceptions
class CalendarError(SmartSaludException):
    """Google Calendar error."""
    pass


class CalendarEventNotFoundError(CalendarError):
    """Calendar event not found."""
    pass


class CalendarSyncError(CalendarError):
    """Calendar sync operation failed."""
    pass


# Scheduler Exceptions
class SchedulerError(SmartSaludException):
    """Scheduler task error."""
    pass


class ReminderSendError(SchedulerError):
    """Failed to send scheduled reminder."""
    pass
