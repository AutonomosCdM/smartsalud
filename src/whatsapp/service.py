"""
Twilio API service wrapper.

Handles sending WhatsApp messages via Twilio.
"""
from twilio.rest import Client

from src.core.config import settings


class TwilioService:
    """Twilio WhatsApp service."""

    def __init__(self):
        self.client = Client(
            settings.twilio_account_sid,
            settings.twilio_auth_token
        )
        self.whatsapp_number = settings.twilio_whatsapp_number

    async def send_message(self, to: str, body: str) -> str:
        """
        Send WhatsApp message.

        Args:
            to: Recipient phone number (format: whatsapp:+56912345678)
            body: Message content

        Returns:
            Message SID
        """
        # Ensure whatsapp: prefix
        if not to.startswith("whatsapp:"):
            to = f"whatsapp:{to}"

        message = self.client.messages.create(
            from_=self.whatsapp_number,
            to=to,
            body=body
        )

        return message.sid

    async def send_reminder(self, to: str, template_data: dict) -> str:
        """
        Send reminder using Twilio Content Template.

        Args:
            to: Recipient phone number
            template_data: Data for template variables

        Returns:
            Message SID
        """
        # TODO: Implement in Phase 4
        pass


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

_twilio_service = None

def get_twilio_service() -> TwilioService:
    """Get singleton Twilio service instance."""
    global _twilio_service
    if _twilio_service is None:
        _twilio_service = TwilioService()
    return _twilio_service


async def send_whatsapp_message(to: str, body: str) -> str:
    """
    Send WhatsApp message (convenience function).

    Args:
        to: Recipient phone number (with or without whatsapp: prefix)
        body: Message text

    Returns:
        Message SID
    """
    service = get_twilio_service()
    return await service.send_message(to, body)
