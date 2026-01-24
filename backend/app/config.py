from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    # Unifi Controller
    unifi_host: str = ""
    unifi_username: str = ""
    unifi_password: str = ""
    unifi_site: str = "default"
    unifi_verify_ssl: bool = False
    unifi_enabled: bool = True

    # Proxmox
    proxmox_host: str = ""
    proxmox_user: str = ""
    proxmox_token_name: str = ""
    proxmox_token_value: str = ""
    proxmox_node: str = "pve"
    proxmox_verify_ssl: bool = False
    proxmox_enabled: bool = True

    # Plex
    plex_url: str = ""
    plex_token: str = ""
    plex_enabled: bool = True

    # Docker
    docker_host: Optional[str] = None
    docker_enabled: bool = True

    # Google Calendar
    google_credentials_path: str = ""
    google_calendar_ids: str = "primary"
    calendar_enabled: bool = True

    # Weather (Open-Meteo - no API key required)
    weather_latitude: float = 0.0
    weather_longitude: float = 0.0
    weather_enabled: bool = True

    # News (NewsAPI.org)
    news_api_key: str = ""
    news_country: str = "us"
    news_enabled: bool = True

    # UNRAID
    unraid_host: str = ""
    unraid_username: str = ""
    unraid_password: str = ""
    unraid_verify_ssl: bool = False
    unraid_enabled: bool = True

    # Application Settings
    poll_interval: int = 30
    cache_ttl: int = 25
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def calendar_ids_list(self) -> List[str]:
        return [cal.strip() for cal in self.google_calendar_ids.split(",")]

    class Config:
        # In Docker, read from persistent config volume
        # Check both locations - config volume first, then default
        env_file = "/app/config/.env" if Path("/app/config").exists() else ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
