import httpx
from datetime import datetime
import logging

from app.config import get_settings
from app.models.schemas import NewsStatus, NewsHeadline, StatusLevel
from app.services.cache import cache_service
from app.utils.runtime_config import get_service_enabled

logger = logging.getLogger(__name__)

CACHE_KEY = "news_status"


class NewsService:
    def __init__(self):
        self.base_url = "https://newsapi.org/v2/top-headlines"

    async def get_status(self, use_cache: bool = True) -> NewsStatus:
        """Get top headlines from NewsAPI."""
        # Check if service is disabled (from runtime config)
        if not get_service_enabled("news"):
            return NewsStatus(
                status=StatusLevel.UNKNOWN,
                error_message="Service disabled",
                last_updated=datetime.now(),
            )

        if use_cache:
            cached = await cache_service.get(CACHE_KEY)
            if cached:
                return cached

        settings = get_settings()

        if not settings.news_api_key:
            return NewsStatus(
                status=StatusLevel.UNKNOWN,
                error_message="News API key not configured",
                last_updated=datetime.now(),
            )

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {
                    "apiKey": settings.news_api_key,
                    "country": settings.news_country,
                    "pageSize": 5,
                }

                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()

                if data.get("status") != "ok":
                    raise Exception(data.get("message", "Unknown error from NewsAPI"))

                articles = data.get("articles", [])
                headlines = []

                for article in articles[:5]:
                    headline = NewsHeadline(
                        title=article.get("title", ""),
                        source=article.get("source", {}).get("name"),
                        url=article.get("url"),
                    )
                    headlines.append(headline)

                result = NewsStatus(
                    status=StatusLevel.HEALTHY,
                    headlines=headlines,
                    last_updated=datetime.now(),
                )

                await cache_service.set(CACHE_KEY, result)
                return result

        except Exception as e:
            logger.error(f"News error: {e}")
            return NewsStatus(
                status=StatusLevel.ERROR,
                error_message=str(e),
                last_updated=datetime.now(),
            )


news_service = NewsService()
