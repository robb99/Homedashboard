import httpx
from datetime import datetime
import logging

from app.config import get_settings
from app.models.schemas import PlexStatus, PlexItem, StatusLevel
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
                        thumb_url = f"{self.settings.plex_url}{thumb_path}"
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

                # Get library sections count
                sections_url = f"{self.settings.plex_url}/library/sections"
                sections_response = await client.get(sections_url, headers=headers)
                sections_data = sections_response.json()
                library_count = len(
                    sections_data.get("MediaContainer", {}).get("Directory", [])
                )

                result = PlexStatus(
                    status=StatusLevel.HEALTHY,
                    recent_items=recent_items,
                    library_count=library_count,
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
