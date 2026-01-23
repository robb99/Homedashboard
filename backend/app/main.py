import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import get_settings
from app.routers.dashboard import router as dashboard_router
from app.routers.config import router as config_router
from app.routers.logs import router as logs_router
from app.routers.quotes import router as quotes_router
from app.services import (
    unifi_service,
    proxmox_service,
    plex_service,
    docker_service,
    calendar_service,
)
from app.utils.log_buffer import log_buffer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
logging.getLogger().addHandler(log_buffer)

# Scheduler for background tasks
scheduler = AsyncIOScheduler()


async def poll_services():
    """Background task to poll all enabled services."""
    settings = get_settings()
    logger.info("Polling enabled services...")
    try:
        if settings.unifi_enabled:
            await unifi_service.get_status(use_cache=False)
        if settings.proxmox_enabled:
            await proxmox_service.get_status(use_cache=False)
        if settings.plex_enabled:
            await plex_service.get_status(use_cache=False)
        if settings.docker_enabled:
            await docker_service.get_status(use_cache=False)
        if settings.calendar_enabled:
            await calendar_service.get_status(use_cache=False)
        logger.info("Polling complete")
    except Exception as e:
        logger.error(f"Error during polling: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    settings = get_settings()

    # Start scheduler
    scheduler.add_job(
        poll_services,
        "interval",
        seconds=settings.poll_interval,
        id="poll_services",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(f"Scheduler started with {settings.poll_interval}s interval")

    # Initial poll
    await poll_services()

    yield

    # Shutdown
    scheduler.shutdown()
    logger.info("Scheduler stopped")


# Create FastAPI app
app = FastAPI(
    title="HomeLab Dashboard API",
    description="API for monitoring homelab services",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard_router)
app.include_router(config_router)
app.include_router(logs_router)
app.include_router(quotes_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "HomeLab Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
    }
