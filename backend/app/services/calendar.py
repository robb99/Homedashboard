from datetime import datetime, timedelta, date, time, timezone
import logging
import os.path

from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from app.config import get_settings
from app.models.schemas import CalendarStatus, CalendarEvent, StatusLevel
from app.services.cache import cache_service

logger = logging.getLogger(__name__)

CACHE_KEY = "calendar_status"
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


class CalendarService:
    def __init__(self):
        self.settings = get_settings()
        self._service = None

    def _get_credentials(self):
        """Get Google API credentials."""
        creds_path = self.settings.google_credentials_path

        if not creds_path or not os.path.exists(creds_path):
            return None

        try:
            # Try service account first
            if "service_account" in open(creds_path).read():
                creds = service_account.Credentials.from_service_account_file(
                    creds_path, scopes=SCOPES
                )
                return creds

            # OAuth2 credentials
            creds = None
            token_path = creds_path.replace(".json", "_token.json")

            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                    creds = flow.run_local_server(port=0)

                with open(token_path, "w") as token:
                    token.write(creds.to_json())

            return creds

        except Exception as e:
            logger.error(f"Failed to get Google credentials: {e}")
            return None

    def _get_service(self):
        """Get Google Calendar API service."""
        if self._service is None:
            creds = self._get_credentials()
            if creds:
                self._service = build("calendar", "v3", credentials=creds)
        return self._service

    async def get_status(self, use_cache: bool = True) -> CalendarStatus:
        """Get upcoming calendar events for the next 7 days."""
        if use_cache:
            cached = await cache_service.get(CACHE_KEY)
            if cached:
                return cached

        if not self.settings.google_credentials_path:
            return CalendarStatus(
                status=StatusLevel.UNKNOWN,
                error_message="Google Calendar not configured",
                last_updated=datetime.now(),
            )

        try:
            service = self._get_service()
            if service is None:
                return CalendarStatus(
                    status=StatusLevel.ERROR,
                    error_message="Failed to initialize Google Calendar service",
                    last_updated=datetime.now(),
                )

            now = datetime.now(timezone.utc)
            time_min = now.isoformat()
            time_max = (now + timedelta(days=7)).isoformat()

            all_events = []

            for calendar_id in self.settings.calendar_ids_list:
                try:
                    # Get calendar name
                    calendar = service.calendars().get(calendarId=calendar_id).execute()
                    calendar_name = calendar.get("summary", calendar_id)

                    # Get events
                    events_result = (
                        service.events()
                        .list(
                            calendarId=calendar_id,
                            timeMin=time_min,
                            timeMax=time_max,
                            maxResults=50,
                            singleEvents=True,
                            orderBy="startTime",
                        )
                        .execute()
                    )

                    events = events_result.get("items", [])

                    for event in events:
                        start = event.get("start", {})
                        end = event.get("end", {})

                        # Handle all-day events vs timed events
                        if "date" in start:
                            # All-day event: date-only -> make it UTC-aware at midnight
                            start_d = date.fromisoformat(start["date"])
                            end_d = date.fromisoformat(end["date"])
                            start_dt = datetime.combine(start_d, time.min, tzinfo=timezone.utc)
                            end_dt = datetime.combine(end_d, time.min, tzinfo=timezone.utc)
                            all_day = True
                        else: 
                            start_str = start.get("dateTime", "")
                            end_str = end.get("dateTime", "")
                            # Handle timezone offset
                            start_dt = datetime.fromisoformat(
                                start_str.replace("Z", "+00:00")
                            ).astimezone(timezone.utc)
                            end_dt = datetime.fromisoformat(
                                end_str.replace("Z", "+00:00")
                            ).astimezone(timezone.utc)
                            all_day = False

                        calendar_event = CalendarEvent(
                            id=event.get("id", ""),
                            summary=event.get("summary", "No Title"),
                            start=start_dt,
                            end=end_dt,
                            all_day=all_day,
                            location=event.get("location"),
                            calendar_name=calendar_name,
                        )
                        all_events.append(calendar_event)

                except Exception as e:
                    logger.warning(f"Error fetching calendar {calendar_id}: {e}")

            # Sort by start time
            all_events.sort(key=lambda x: x.start)

            result = CalendarStatus(
                status=StatusLevel.HEALTHY if all_events else StatusLevel.UNKNOWN,
                events=all_events,
                event_count=len(all_events),
                last_updated=datetime.now(timezone.utc),
            )

            await cache_service.set(CACHE_KEY, result)
            return result

        except Exception as e:
            logger.error(f"Calendar error: {e}")
            return CalendarStatus(
                status=StatusLevel.ERROR,
                error_message=str(e),
                last_updated=datetime.now(),
            )


calendar_service = CalendarService()
