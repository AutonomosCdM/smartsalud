"""
Google Calendar service.

Handles CRUD operations for calendar events.
"""
from datetime import datetime
from typing import Optional
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import structlog

from src.core.config import settings
from src.calendar.colors import get_color_for_status

logger = structlog.get_logger(__name__)


class CalendarService:
    """Google Calendar service wrapper."""

    def __init__(self):
        self.credentials = self._load_credentials()
        if self.credentials:
            self.service = build("calendar", "v3", credentials=self.credentials)
        else:
            self.service = None
            logger.warning(
                "calendar_service_not_initialized",
                message="No credentials available. Calendar sync disabled."
            )

    def _load_credentials(self) -> Optional[Credentials]:
        """
        Load Google Calendar OAuth2 credentials.

        Looks for token.json file in project root. If credentials are expired,
        attempts to refresh them automatically.

        Returns:
            Credentials object if available, None otherwise
        """
        try:
            # Get project root
            project_root = Path(__file__).parent.parent.parent
            token_file = project_root / settings.google_calendar_credentials_file

            if not token_file.exists():
                logger.warning(
                    "calendar_token_not_found",
                    token_file=str(token_file),
                    message="Run scripts/setup_google_calendar.py to authenticate"
                )
                return None

            # Load credentials
            creds = Credentials.from_authorized_user_file(
                str(token_file),
                scopes=[settings.google_calendar_scopes]
            )

            # Refresh if expired
            if creds.expired and creds.refresh_token:
                logger.info("calendar_token_expired", message="Refreshing token...")
                creds.refresh(Request())

                # Save refreshed token
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())

                logger.info("calendar_token_refreshed")

            logger.info("calendar_credentials_loaded")
            return creds

        except Exception as e:
            logger.error(
                "failed_to_load_calendar_credentials",
                error=str(e),
                exc_info=True
            )
            return None

    async def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        status: str = "PENDING",
        calendar_id: str = "primary",
        attendees: Optional[list] = None
    ) -> Optional[str]:
        """
        Create calendar event.

        Args:
            summary: Event title (e.g., "Cita - Dr. González")
            start_time: Event start time
            end_time: Event end time
            description: Event description
            status: Appointment status for color
            calendar_id: Calendar ID (default: "primary")

        Returns:
            Event ID if successful, None otherwise
        """
        if not self.service:
            logger.warning("calendar_service_unavailable", action="create_event")
            return None

        try:
            # Get color for status
            color_id = get_color_for_status(status)

            # Build event object
            event = {
                'summary': summary,
                'description': description or '',
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'America/Santiago',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'America/Santiago',
                },
                'colorId': color_id,
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 24 * 60},  # 1 día antes
                        {'method': 'popup', 'minutes': 60},        # 1 hora antes
                    ],
                },
            }

            # Add attendees if provided
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]

            # Create event
            result = self.service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()

            event_id = result.get('id')

            logger.info(
                "calendar_event_created",
                event_id=event_id,
                summary=summary,
                start_time=start_time.isoformat(),
                color_id=color_id,
                status=status
            )

            return event_id

        except HttpError as e:
            logger.error(
                "failed_to_create_calendar_event",
                error=str(e),
                summary=summary,
                exc_info=True
            )
            return None
        except Exception as e:
            logger.error(
                "unexpected_error_creating_calendar_event",
                error=str(e),
                exc_info=True
            )
            return None

    async def update_event_color(
        self,
        event_id: str,
        status: str,
        calendar_id: str = "primary"
    ) -> bool:
        """
        Update calendar event color based on status.

        Args:
            event_id: Google Calendar event ID
            status: New appointment status
            calendar_id: Calendar ID (default: "primary")

        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            logger.warning("calendar_service_unavailable", action="update_event_color")
            return False

        color_id = get_color_for_status(status)

        try:
            # Get existing event
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            # Update color
            event['colorId'] = color_id

            # Update event
            self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()

            logger.info(
                "calendar_event_color_updated",
                event_id=event_id,
                status=status,
                color_id=color_id
            )

            return True

        except HttpError as e:
            if e.resp.status == 404:
                logger.warning(
                    "calendar_event_not_found",
                    event_id=event_id,
                    message="Event may have been deleted"
                )
            else:
                logger.error(
                    "failed_to_update_calendar_event_color",
                    error=str(e),
                    event_id=event_id,
                    exc_info=True
                )
            return False
        except Exception as e:
            logger.error(
                "unexpected_error_updating_calendar_event",
                error=str(e),
                event_id=event_id,
                exc_info=True
            )
            return False

    async def delete_event(
        self,
        event_id: str,
        calendar_id: str = "primary"
    ) -> bool:
        """
        Delete calendar event.

        Args:
            event_id: Google Calendar event ID
            calendar_id: Calendar ID (default: "primary")

        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            logger.warning("calendar_service_unavailable", action="delete_event")
            return False

        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            logger.info(
                "calendar_event_deleted",
                event_id=event_id
            )

            return True

        except HttpError as e:
            if e.resp.status == 404:
                logger.warning(
                    "calendar_event_not_found_for_deletion",
                    event_id=event_id,
                    message="Event may have already been deleted"
                )
                # Consider this a success since the end result is the same
                return True
            else:
                logger.error(
                    "failed_to_delete_calendar_event",
                    error=str(e),
                    event_id=event_id,
                    exc_info=True
                )
                return False
        except Exception as e:
            logger.error(
                "unexpected_error_deleting_calendar_event",
                error=str(e),
                event_id=event_id,
                exc_info=True
            )
            return False
