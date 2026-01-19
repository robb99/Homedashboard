from cachetools import TTLCache
from typing import Any, Optional
from datetime import datetime
import asyncio

from app.config import get_settings


class CacheService:
    """Simple in-memory cache with TTL support."""

    def __init__(self):
        settings = get_settings()
        self._cache = TTLCache(maxsize=100, ttl=settings.cache_ttl)
        self._lock = asyncio.Lock()
        self._timestamps: dict[str, datetime] = {}

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            return self._cache.get(key)

    async def set(self, key: str, value: Any) -> None:
        async with self._lock:
            self._cache[key] = value
            self._timestamps[key] = datetime.now()

    async def get_timestamp(self, key: str) -> Optional[datetime]:
        async with self._lock:
            return self._timestamps.get(key)

    async def clear(self) -> None:
        async with self._lock:
            self._cache.clear()
            self._timestamps.clear()


# Singleton instance
cache_service = CacheService()
