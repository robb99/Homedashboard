from fastapi import APIRouter
from datetime import datetime

from app.config import get_settings
from app.models.schemas import (
    DashboardStatus,
    UnifiStatus,
    ProxmoxStatus,
    PlexStatus,
    DockerStatus,
    CalendarStatus,
    WeatherStatus,
    NewsStatus,
    UnraidStatus,
    StatusLevel,
)
from app.services import (
    unifi_service,
    proxmox_service,
    plex_service,
    docker_service,
    calendar_service,
    weather_service,
    news_service,
    unraid_service,
)

router = APIRouter(prefix="/api", tags=["dashboard"])


def _disabled_status(status_cls):
    return status_cls(
        status=StatusLevel.UNKNOWN,
        error_message="Service disabled",
        last_updated=datetime.now(),
    )


@router.get("/dashboard", response_model=DashboardStatus)
async def get_dashboard():
    """Get complete dashboard status from all enabled services."""
    settings = get_settings()

    # Only fetch enabled services, return disabled status for others
    if settings.unifi_enabled:
        unifi = await unifi_service.get_status()
    else:
        unifi = _disabled_status(UnifiStatus)

    if settings.proxmox_enabled:
        proxmox = await proxmox_service.get_status()
    else:
        proxmox = _disabled_status(ProxmoxStatus)

    if settings.plex_enabled:
        plex = await plex_service.get_status()
    else:
        plex = _disabled_status(PlexStatus)

    if settings.docker_enabled:
        docker = await docker_service.get_status()
    else:
        docker = _disabled_status(DockerStatus)

    if settings.calendar_enabled:
        calendar = await calendar_service.get_status()
    else:
        calendar = _disabled_status(CalendarStatus)

    if settings.unraid_enabled:
        unraid = await unraid_service.get_status()
    else:
        unraid = _disabled_status(UnraidStatus)

    return DashboardStatus(
        unifi=unifi,
        proxmox=proxmox,
        plex=plex,
        docker=docker,
        calendar=calendar,
        unraid=unraid,
        last_updated=datetime.now(),
    )


@router.get("/unifi", response_model=UnifiStatus)
async def get_unifi():
    """Get Unifi controller status."""
    return await unifi_service.get_status()


@router.get("/proxmox", response_model=ProxmoxStatus)
async def get_proxmox():
    """Get Proxmox status."""
    return await proxmox_service.get_status()


@router.get("/plex", response_model=PlexStatus)
async def get_plex():
    """Get Plex recently added."""
    return await plex_service.get_status()


@router.get("/docker", response_model=DockerStatus)
async def get_docker():
    """Get Docker container status."""
    return await docker_service.get_status()


@router.get("/calendar", response_model=CalendarStatus)
async def get_calendar():
    """Get upcoming calendar events."""
    return await calendar_service.get_status()


@router.get("/weather", response_model=WeatherStatus)
async def get_weather():
    """Get weather forecast from Open-Meteo."""
    return await weather_service.get_status()


@router.get("/news", response_model=NewsStatus)
async def get_news():
    """Get top headlines from NewsAPI."""
    return await news_service.get_status()


@router.get("/unraid", response_model=UnraidStatus)
async def get_unraid():
    """Get Unraid server status."""
    return await unraid_service.get_status()


@router.post("/refresh")
async def refresh_all():
    """Force refresh all cached data for enabled services."""
    from app.services.cache import cache_service

    settings = get_settings()
    await cache_service.clear()

    # Fetch fresh data for enabled services only
    services = [
        (settings.unifi_enabled, unifi_service),
        (settings.proxmox_enabled, proxmox_service),
        (settings.plex_enabled, plex_service),
        (settings.docker_enabled, docker_service),
        (settings.calendar_enabled, calendar_service),
        (settings.unraid_enabled, unraid_service),
    ]
    for enabled, service in services:
        if enabled:
            await service.get_status(use_cache=False)

    return {"status": "refreshed", "timestamp": datetime.now().isoformat()}


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
