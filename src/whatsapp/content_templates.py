"""
Twilio Content Template management for WhatsApp interactive messages.

Handles creation and management of Content Templates with Quick Reply buttons.
"""
from typing import Optional, Dict, Any, List
import json
import requests
from twilio.rest import Client
import structlog
from src.core.config import get_settings

logger = structlog.get_logger(__name__)


class ContentTemplateService:
    """Service for managing Twilio Content Templates with interactive buttons."""

    def __init__(self):
        """Initialize Twilio client."""
        settings = get_settings()
        self.client = Client(self.twilio_account_sid, self.twilio_auth_token)
        self.twilio_account_sid = self.twilio_account_sid
        self.twilio_auth_token = self.twilio_auth_token
        self.twilio_whatsapp_number = self.twilio_whatsapp_number

    def create_appointment_reminder_template(self) -> str:
        """
        Create Content Template for appointment reminders with Quick Reply buttons.

        Uses REST API directly since Python SDK doesn't support template creation yet.

        Returns:
            Content SID of the created template

        Note:
            Template includes 2 quick reply buttons: Confirmar and Cancelar
            Maximum 3 buttons allowed for WhatsApp in-session messages
        """
        try:
            # Twilio Content API endpoint
            url = f"https://content.twilio.com/v1/Content"

            # Define template payload
            payload = {
                "friendly_name": "appointment_reminder_buttons",
                "language": "es",
                "variables": {
                    "1": "Nombre del paciente",
                    "2": "24 de Octubre 2025, 14:30",
                    "3": "Dr. Andrea Silva",
                    "4": "Medicina General"
                },
                "types": {
                    "twilio/quick-reply": {
                        "body": "¡Hola {{1}}! 👋\n\nTienes una cita pendiente:\n📅 Fecha: {{2}}\n👨‍⚕️ Doctor: {{3}}\n🏥 Especialidad: {{4}}",
                        "actions": [
                            {
                                "id": "CONFIRM",
                                "title": "✅ Confirmar"
                            },
                            {
                                "id": "CANCEL",
                                "title": "❌ Cancelar"
                            }
                        ]
                    }
                }
            }

            # Make API request with Basic Auth
            response = requests.post(
                url,
                auth=(self.twilio_account_sid, self.twilio_auth_token),
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )

            response.raise_for_status()
            result = response.json()

            content_sid = result["sid"]

            logger.info(
                "content_template_created",
                content_sid=content_sid,
                friendly_name=result.get("friendly_name")
            )

            return content_sid

        except requests.exceptions.HTTPError as e:
            logger.error(
                "failed_to_create_content_template",
                error=str(e),
                response_body=e.response.text if e.response else None
            )
            raise
        except Exception as e:
            logger.error(
                "failed_to_create_content_template",
                error=str(e)
            )
            raise

    def send_message_with_buttons(
        self,
        to: str,
        content_sid: str,
        patient_name: str,
        appointment_date: str,
        doctor_name: str,
        specialty: str
    ) -> str:
        """
        Send WhatsApp message with interactive buttons using Content Template.

        Args:
            to: Recipient WhatsApp number (format: whatsapp:+56912345678)
            content_sid: Content Template SID
            patient_name: Patient's first name
            appointment_date: Formatted appointment date/time
            doctor_name: Doctor's full name
            specialty: Medical specialty

        Returns:
            Twilio Message SID
        """
        try:
            # Prepare content variables for template
            content_variables = {
                "1": patient_name,
                "2": appointment_date,
                "3": doctor_name,
                "4": specialty
            }

            # Send message with content template
            message = self.client.messages.create(
                from_=self.twilio_whatsapp_number,
                to=to,
                content_sid=content_sid,
                content_variables=json.dumps(content_variables)  # Must be JSON string
            )

            logger.info(
                "message_sent_with_buttons",
                message_sid=message.sid,
                to=to,
                content_sid=content_sid
            )

            return message.sid

        except Exception as e:
            logger.error(
                "failed_to_send_message_with_buttons",
                error=str(e),
                to=to
            )
            raise

    def get_or_create_reminder_template(self) -> str:
        """
        Get existing appointment reminder template or create new one.

        Returns:
            Content SID of the template

        Note:
            Caches the ContentSID to avoid recreating templates
            For production, store ContentSID in database or env variable
        """
        # For now, create new template
        # TODO: Cache ContentSID in database or config after first creation
        return self.create_appointment_reminder_template()

    def create_reschedule_prompt_template(self) -> str:
        """
        Create Content Template for asking if user wants to reschedule.

        Returns:
            Content SID of the created template

        Note:
            Template includes 2 quick reply buttons: Sí, reagendar and No, gracias
        """
        try:
            url = f"https://content.twilio.com/v1/Content"

            payload = {
                "friendly_name": "reschedule_prompt",
                "language": "es",
                "variables": {
                    "1": "Nombre del paciente"
                },
                "types": {
                    "twilio/quick-reply": {
                        "body": "❌ Cita cancelada exitosamente, {{1}}.\n\n¿Deseas reagendar tu cita?",
                        "actions": [
                            {
                                "id": "YES_RESCHEDULE",
                                "title": "✅ Sí, reagendar"
                            },
                            {
                                "id": "NO_RESCHEDULE",
                                "title": "❌ No, gracias"
                            }
                        ]
                    }
                }
            }

            response = requests.post(
                url,
                auth=(self.twilio_account_sid, self.twilio_auth_token),
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )

            response.raise_for_status()
            result = response.json()

            content_sid = result["sid"]

            logger.info(
                "reschedule_prompt_template_created",
                content_sid=content_sid
            )

            return content_sid

        except requests.exceptions.HTTPError as e:
            logger.error(
                "failed_to_create_reschedule_template",
                error=str(e),
                response_body=e.response.text if e.response else None
            )
            raise
        except Exception as e:
            logger.error(
                "failed_to_create_reschedule_template",
                error=str(e)
            )
            raise

    def send_reschedule_prompt(
        self,
        to: str,
        patient_name: str,
        content_sid: Optional[str] = None
    ) -> str:
        """
        Send reschedule prompt with Yes/No buttons.

        Args:
            to: Recipient WhatsApp number
            patient_name: Patient's first name
            content_sid: Optional Content SID (creates new if not provided)

        Returns:
            Twilio Message SID
        """
        try:
            # Create template if not provided
            if not content_sid:
                content_sid = self.create_reschedule_prompt_template()

            content_variables = {
                "1": patient_name
            }

            message = self.client.messages.create(
                from_=self.twilio_whatsapp_number,
                to=to,
                content_sid=content_sid,
                content_variables=json.dumps(content_variables)
            )

            logger.info(
                "reschedule_prompt_sent",
                message_sid=message.sid,
                to=to
            )

            return message.sid

        except Exception as e:
            logger.error(
                "failed_to_send_reschedule_prompt",
                error=str(e),
                to=to
            )
            raise

    def send_goodbye_message(self, to: str, patient_name: str) -> str:
        """
        Send goodbye message when user declines to reschedule.

        Args:
            to: Recipient WhatsApp number
            patient_name: Patient's first name

        Returns:
            Twilio Message SID
        """
        try:
            goodbye_text = f"""¡Muchas gracias, {patient_name}! 👋

Si necesitas algo más, no dudes en contactarnos.

CESFAM Futrono"""

            message = self.client.messages.create(
                from_=self.twilio_whatsapp_number,
                to=to,
                body=goodbye_text
            )

            logger.info(
                "goodbye_message_sent",
                message_sid=message.sid,
                to=to
            )

            return message.sid

        except Exception as e:
            logger.error(
                "failed_to_send_goodbye_message",
                error=str(e),
                to=to
            )
            raise

    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List all Content Templates in the account.

        Returns:
            List of template information dictionaries
        """
        try:
            templates = self.client.content.v1.contents.list()

            template_list = [
                {
                    "sid": t.sid,
                    "friendly_name": t.friendly_name,
                    "language": t.language,
                    "date_created": t.date_created
                }
                for t in templates
            ]

            logger.info(
                "templates_listed",
                count=len(template_list)
            )

            return template_list

        except Exception as e:
            logger.error(
                "failed_to_list_templates",
                error=str(e)
            )
            raise

    def create_timeslot_options_template(self) -> str:
        """
        Create Content Template for showing available timeslot options.

        Returns:
            Content SID of the created template

        Note:
            Template includes 3 quick reply buttons for available time slots
        """
        try:
            url = f"https://content.twilio.com/v1/Content"

            payload = {
                "friendly_name": "timeslot_options",
                "language": "es",
                "variables": {
                    "1": "Nombre del paciente",
                    "2": "Opción 1 de horario",
                    "3": "Opción 2 de horario",
                    "4": "Opción 3 de horario"
                },
                "types": {
                    "twilio/quick-reply": {
                        "body": "Perfecto, {{1}}! 📅\n\nElige tu nuevo horario:\n\n📍 Opción 1: {{2}}\n📍 Opción 2: {{3}}\n📍 Opción 3: {{4}}",
                        "actions": [
                            {
                                "id": "SLOT_1",
                                "title": "📅 Opción 1"
                            },
                            {
                                "id": "SLOT_2",
                                "title": "📅 Opción 2"
                            },
                            {
                                "id": "SLOT_3",
                                "title": "📅 Opción 3"
                            }
                        ]
                    }
                }
            }

            response = requests.post(
                url,
                auth=(self.twilio_account_sid, self.twilio_auth_token),
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )

            response.raise_for_status()
            result = response.json()

            content_sid = result["sid"]

            logger.info(
                "timeslot_options_template_created",
                content_sid=content_sid
            )

            return content_sid

        except requests.exceptions.HTTPError as e:
            logger.error(
                "failed_to_create_timeslot_template",
                error=str(e),
                response_body=e.response.text if e.response else None
            )
            raise
        except Exception as e:
            logger.error(
                "failed_to_create_timeslot_template",
                error=str(e)
            )
            raise

    def send_timeslot_options(
        self,
        to: str,
        patient_name: str,
        slots: List[Dict[str, Any]],
        content_sid: Optional[str] = None
    ) -> str:
        """
        Send timeslot options with buttons.

        Args:
            to: Recipient WhatsApp number
            patient_name: Patient's first name
            slots: List of slot dictionaries with 'display' keys (expects 3 slots)
            content_sid: Optional Content SID (creates new if not provided)

        Returns:
            Twilio Message SID
        """
        try:
            # Create template if not provided
            if not content_sid:
                content_sid = self.create_timeslot_options_template()

            # Extract display values from slots
            slot1_display = slots[0]["display"] if len(slots) > 0 else "No disponible"
            slot2_display = slots[1]["display"] if len(slots) > 1 else "No disponible"
            slot3_display = slots[2]["display"] if len(slots) > 2 else "No disponible"

            content_variables = {
                "1": patient_name,
                "2": slot1_display,
                "3": slot2_display,
                "4": slot3_display
            }

            message = self.client.messages.create(
                from_=self.twilio_whatsapp_number,
                to=to,
                content_sid=content_sid,
                content_variables=json.dumps(content_variables)
            )

            logger.info(
                "timeslot_options_sent",
                message_sid=message.sid,
                to=to,
                slot1=slot1_display,
                slot2=slot2_display,
                slot3=slot3_display
            )

            return message.sid

        except Exception as e:
            logger.error(
                "failed_to_send_timeslot_options",
                error=str(e),
                to=to
            )
            raise
