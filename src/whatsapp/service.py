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
        # TODO: Implement in Phase 2
        pass

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
