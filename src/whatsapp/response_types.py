"""
Response types for WhatsApp handlers.

Allows handlers to return structured responses with actions like sending buttons.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class ResponseAction(Enum):
    """Actions that can be taken after a handler completes."""
    SEND_TEXT = "send_text"  # Just send text response
    SEND_RESCHEDULE_BUTTONS = "send_reschedule_buttons"  # Ask if want to reschedule
    SEND_TIMESLOT_BUTTONS = "send_timeslot_buttons"  # Show available time slots
    SEND_GOODBYE = "send_goodbye"  # Send goodbye message


@dataclass
class HandlerResponse:
    """
    Structured response from a WhatsApp handler.

    Attributes:
        message: Text message to send (may be None if using content template)
        action: Action to take (default: send text)
        data: Additional data for the action (e.g., patient info, appointment details)
    """
    message: Optional[str] = None
    action: ResponseAction = ResponseAction.SEND_TEXT
    data: Optional[Dict[str, Any]] = None

    @classmethod
    def text(cls, message: str) -> "HandlerResponse":
        """Create a simple text response."""
        return cls(message=message, action=ResponseAction.SEND_TEXT)

    @classmethod
    def reschedule_prompt(cls, patient_name: str, phone: str) -> "HandlerResponse":
        """Create a response that asks if user wants to reschedule."""
        return cls(
            action=ResponseAction.SEND_RESCHEDULE_BUTTONS,
            data={
                "patient_name": patient_name,
                "phone": phone
            }
        )

    @classmethod
    def timeslot_options(cls, patient_name: str, phone: str, slots: list) -> "HandlerResponse":
        """Create a response that shows available time slots."""
        return cls(
            action=ResponseAction.SEND_TIMESLOT_BUTTONS,
            data={
                "patient_name": patient_name,
                "phone": phone,
                "slots": slots
            }
        )

    @classmethod
    def goodbye(cls, patient_name: str) -> "HandlerResponse":
        """Create a goodbye response."""
        return cls(
            action=ResponseAction.SEND_GOODBYE,
            data={"patient_name": patient_name}
        )
