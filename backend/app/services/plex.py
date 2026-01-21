import httpx
from datetime import datetime
import logging

from app.config import get_settings
from app.models.schemas import PlexStatus, PlexItem, PlexSession, StatusLevel
from app.services.cache import cache_service

logger = logging.getLogger(__name__)

CACHE_KEY = "plex_status"


class PlexService:
    def __init__(self):
        self.settings = get_settings()

    async def get_status(self, use_cache: bool = True) -> PlexStatus:
        """Get Plex recently added items."""
        if use_cache:
            cached = await cache_service.get(CACHE_KEY)
            if cached:
                return cached

        if not self.settings.plex_url or not self.settings.plex_token:
            return PlexStatus(
                status=StatusLevel.UNKNOWN,
                error_message="Plex not configured",
                last_updated=datetime.now(),
            )

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {
                    "X-Plex-Token": self.settings.plex_token,
                    "Accept": "application/json",
                }

                # Get recently added
                recent_url = f"{self.settings.plex_url}/library/recentlyAdded"
                response = await client.get(recent_url, headers=headers)
                data = response.json()

                media_container = data.get("MediaContainer", {})
                metadata = media_container.get("Metadata", [])

                recent_items = []
                for item in metadata[:10]:  # Limit to 10 items
                    added_at = datetime.fromtimestamp(item.get("addedAt", 0))

                    thumb_path = item.get("thumb") or item.get("grandparentThumb")
                    if thumb_path:
                        # Plex often returns relative URLs for thumbs, prepend the base URL
                        thumb_url = f"{self.settings.plex_url}{thumb_path}?X-Plex-Token={self.settings.plex_token}"
                    else:
                        thumb_url = None

                    plex_item = PlexItem(
                        title=item.get("title", "Unknown"),
                        type=item.get("type", "unknown"),
                        added_at=added_at,
                        thumb=thumb_url,
                        year=item.get("year"),
                        grandparent_title=item.get("grandparentTitle"),
                        parent_title=item.get("parentTitle"),
                    )
                    recent_items.append(plex_item)

                # Get library sections
                sections_url = f"{self.settings.plex_url}/library/sections"
                sections_response = await client.get(sections_url, headers=headers)
                sections_data = sections_response.json()
                directories = sections_data.get("MediaContainer", {}).get("Directory", [])
                library_count = len(directories)

                # Find movie and show library keys and get counts
                movie_count = 0
                show_count = 0
                for directory in directories:
                    section_type = directory.get("type", "")
                    section_key = directory.get("key", "")
                    if section_type == "movie":
                        # Get movie count - use X-Plex-Container-Size=0 to only get count
                        section_url = f"{self.settings.plex_url}/library/sections/{section_key}/all?X-Plex-Container-Start=0&X-Plex-Container-Size=0"
                        section_response = await client.get(section_url, headers=headers)
                        section_data = section_response.json()
                        container = section_data.get("MediaContainer", {})
                        movie_count += container.get("totalSize", container.get("size", 0))
                    elif section_type == "show":
                        # Get show count - use X-Plex-Container-Size=0 to only get count
                        section_url = f"{self.settings.plex_url}/library/sections/{section_key}/all?X-Plex-Container-Start=0&X-Plex-Container-Size=0"
                        section_response = await client.get(section_url, headers=headers)
                        section_data = section_response.json()
                        container = section_data.get("MediaContainer", {})
                        show_count += container.get("totalSize", container.get("size", 0))

                # Get active sessions
                sessions_url = f"{self.settings.plex_url}/status/sessions"
                sessions_response = await client.get(sessions_url, headers=headers)
                sessions_data = sessions_response.json()
                session_metadata = sessions_data.get("MediaContainer", {}).get("Metadata", [])

                active_sessions = []
                for session in session_metadata:
                    user_info = session.get("User", {})
                    user_name = user_info.get("title", "Unknown")

                    session_type = session.get("type", "unknown")
                    title = session.get("title", "Unknown")
                    show_title = session.get("grandparentTitle") if session_type == "episode" else None

                    # Calculate progress percentage
                    view_offset = session.get("viewOffset", 0)
                    duration = session.get("duration", 1)
                    progress = (view_offset / duration * 100) if duration > 0 else 0

                    # Get playback state
                    player_info = session.get("Player", {})
                    state = player_info.get("state", "playing")

                    active_sessions.append(PlexSession(
                        user=user_name,
                        title=title,
                        show_title=show_title,
                        type=session_type,
                        progress=round(progress, 1),
                        state=state
                    ))

                result = PlexStatus(
                    status=StatusLevel.HEALTHY,
                    recent_items=recent_items,
                    library_count=library_count,
                    movie_count=movie_count,
                    show_count=show_count,
                    active_sessions=active_sessions,
                    last_updated=datetime.now(),
                )

                await cache_service.set(CACHE_KEY, result)
                return result

        except Exception as e:
            logger.error(f"Plex error: {e}")
            return PlexStatus(
                status=StatusLevel.ERROR,
                error_message=str(e),
                last_updated=datetime.now(),
            )


plex_service = PlexService()
