from fastapi import APIRouter
from datetime import datetime

from app.models.schemas import (
    DashboardStatus,
    UnifiStatus,
    ProxmoxStatus,
    PlexStatus,
    DockerStatus,
    CalendarStatus,
)
from app.services import (
    unifi_service,
    proxmox_service,
    plex_service,
    docker_service,
    calendar_service,
)

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardStatus)
async def get_dashboard():
    """Get complete dashboard status from all services."""
    unifi = await unifi_service.get_status()
    proxmox = await proxmox_service.get_status()
    plex = await plex_service.get_status()
    docker = await docker_service.get_status()
    calendar = await calendar_service.get_status()

    return DashboardStatus(
        unifi=unifi,
        proxmox=proxmox,
        plex=plex,
        docker=docker,
        calendar=calendar,
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


@router.post("/refresh")
async def refresh_all():
    """Force refresh all cached data."""
    from app.services.cache import cache_service

    await cache_service.clear()

    # Fetch fresh data
    await unifi_service.get_status(use_cache=False)
    await proxmox_service.get_status(use_cache=False)
    await plex_service.get_status(use_cache=False)
    await docker_service.get_status(use_cache=False)
    await calendar_service.get_status(use_cache=False)

    return {"status": "refreshed", "timestamp": datetime.now().isoformat()}


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
