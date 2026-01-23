"""
Configuration API router for setup wizard.
Provides endpoints for reading/writing config and testing connections.
"""
from fastapi import APIRouter, HTTPException
import logging

from app.config import get_settings
from app.utils.env_manager import read_env, write_env
from app.utils.runtime_config import get_runtime_config, save_runtime_config
from app.services.cache import cache_service
from app.models.schemas import (
    ConfigStatus,
    ServiceConfigStatus,
    ConfigUpdate,
    ConfigResponse,
    TestConnectionRequest,
    TestConnectionResult,
)
from app.services.test_connections import (
    test_unifi_connection,
    test_proxmox_connection,
    test_plex_connection,
    test_docker_connection,
    test_calendar_connection,
    test_weather_connection,
    test_news_connection,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/config", tags=["config"])

# Fields that should be masked in responses
MASKED_FIELDS = {
    "unifi_password",
    "proxmox_token_value",
    "plex_token",
    "news_api_key",
}

MASK_VALUE = "********"


def _is_configured(value: str) -> bool:
    """Check if a config value is set (non-empty)."""
    return bool(value and value.strip())


def _mask_value(key: str, value: str) -> str:
    """Mask sensitive values if set, return empty if not set."""
    if key in MASKED_FIELDS:
        return MASK_VALUE if _is_configured(value) else ""
    return value


@router.get("/status", response_model=ConfigStatus)
async def get_config_status():
    """Get configuration status for all services."""
    settings = get_settings()

    # Check each service's configuration status
    unifi_configured = _is_configured(settings.unifi_host)
    unifi_has_creds = all([
        _is_configured(settings.unifi_username),
        _is_configured(settings.unifi_password),
    ])

    proxmox_configured = _is_configured(settings.proxmox_host)
    proxmox_has_creds = all([
        _is_configured(settings.proxmox_user),
        _is_configured(settings.proxmox_token_name),
        _is_configured(settings.proxmox_token_value),
    ])

    plex_configured = _is_configured(settings.plex_url)
    plex_has_creds = _is_configured(settings.plex_token)

    # Docker: check if explicitly configured via DOCKER_HOST, otherwise not counted as "configured"
    # (local socket auto-detection doesn't count as user configuration)
    docker_configured = _is_configured(settings.docker_host or "")
    docker_has_creds = True  # Docker doesn't need credentials

    calendar_configured = _is_configured(settings.google_credentials_path)
    calendar_has_creds = calendar_configured

    weather_configured = settings.weather_latitude != 0.0 or settings.weather_longitude != 0.0
    weather_has_creds = True  # No auth needed

    news_configured = _is_configured(settings.news_api_key)
    news_has_creds = news_configured

    # First run if no services are configured
    any_service_configured = any([
        unifi_configured and unifi_has_creds,
        proxmox_configured and proxmox_has_creds,
        plex_configured and plex_has_creds,
        calendar_configured,
        weather_configured,
        news_configured,
    ])

    return ConfigStatus(
        is_first_run=not any_service_configured,
        unifi=ServiceConfigStatus(configured=unifi_configured, has_credentials=unifi_has_creds),
        proxmox=ServiceConfigStatus(configured=proxmox_configured, has_credentials=proxmox_has_creds),
        plex=ServiceConfigStatus(configured=plex_configured, has_credentials=plex_has_creds),
        docker=ServiceConfigStatus(configured=docker_configured, has_credentials=docker_has_creds),
        calendar=ServiceConfigStatus(configured=calendar_configured, has_credentials=calendar_has_creds),
        weather=ServiceConfigStatus(configured=weather_configured, has_credentials=weather_has_creds),
        news=ServiceConfigStatus(configured=news_configured, has_credentials=news_has_creds),
    )


@router.get("", response_model=ConfigResponse)
async def get_config():
    """Get current configuration with masked passwords."""
    settings = get_settings()
    runtime_config = get_runtime_config()

    return ConfigResponse(
        # UniFi
        unifi_host=settings.unifi_host,
        unifi_username=settings.unifi_username,
        unifi_password=_mask_value("unifi_password", settings.unifi_password),
        unifi_site=settings.unifi_site,
        unifi_verify_ssl=settings.unifi_verify_ssl,
        unifi_enabled=runtime_config.get("unifi_enabled", True),
        # Proxmox
        proxmox_host=settings.proxmox_host,
        proxmox_user=settings.proxmox_user,
        proxmox_token_name=settings.proxmox_token_name,
        proxmox_token_value=_mask_value("proxmox_token_value", settings.proxmox_token_value),
        proxmox_node=settings.proxmox_node,
        proxmox_verify_ssl=settings.proxmox_verify_ssl,
        proxmox_enabled=runtime_config.get("proxmox_enabled", True),
        # Plex
        plex_url=settings.plex_url,
        plex_token=_mask_value("plex_token", settings.plex_token),
        plex_enabled=runtime_config.get("plex_enabled", True),
        # Docker
        docker_host=settings.docker_host or "",
        docker_enabled=runtime_config.get("docker_enabled", True),
        # Calendar
        google_credentials_path=settings.google_credentials_path,
        google_calendar_ids=settings.google_calendar_ids,
        calendar_enabled=runtime_config.get("calendar_enabled", True),
        # Weather
        weather_latitude=settings.weather_latitude,
        weather_longitude=settings.weather_longitude,
        weather_enabled=runtime_config.get("weather_enabled", True),
        # News
        news_api_key=_mask_value("news_api_key", settings.news_api_key),
        news_country=settings.news_country,
        news_enabled=runtime_config.get("news_enabled", True),
        # Application
        poll_interval=settings.poll_interval,
        cache_ttl=settings.cache_ttl,
        cors_origins=settings.cors_origins,
    )


@router.post("")
async def save_config(config: ConfigUpdate):
    """Save configuration to .env file and runtime config."""
    # Build updates dict for .env, only including non-None values
    updates = {}

    # Build runtime config updates for enabled flags
    runtime_updates = {}

    # Helper to add if not None and not masked placeholder
    def add_if_set(key: str, value, env_key: str = None):
        if value is not None:
            # Skip masked placeholder values
            if isinstance(value, str) and value == MASK_VALUE:
                return
            updates[env_key or key.upper()] = str(value) if not isinstance(value, str) else value

    # UniFi
    add_if_set("unifi_host", config.unifi_host, "UNIFI_HOST")
    add_if_set("unifi_username", config.unifi_username, "UNIFI_USERNAME")
    add_if_set("unifi_password", config.unifi_password, "UNIFI_PASSWORD")
    add_if_set("unifi_site", config.unifi_site, "UNIFI_SITE")
    if config.unifi_verify_ssl is not None:
        updates["UNIFI_VERIFY_SSL"] = str(config.unifi_verify_ssl).lower()
    if config.unifi_enabled is not None:
        runtime_updates["unifi_enabled"] = config.unifi_enabled

    # Proxmox
    add_if_set("proxmox_host", config.proxmox_host, "PROXMOX_HOST")
    add_if_set("proxmox_user", config.proxmox_user, "PROXMOX_USER")
    add_if_set("proxmox_token_name", config.proxmox_token_name, "PROXMOX_TOKEN_NAME")
    add_if_set("proxmox_token_value", config.proxmox_token_value, "PROXMOX_TOKEN_VALUE")
    add_if_set("proxmox_node", config.proxmox_node, "PROXMOX_NODE")
    if config.proxmox_verify_ssl is not None:
        updates["PROXMOX_VERIFY_SSL"] = str(config.proxmox_verify_ssl).lower()
    if config.proxmox_enabled is not None:
        runtime_updates["proxmox_enabled"] = config.proxmox_enabled

    # Plex
    add_if_set("plex_url", config.plex_url, "PLEX_URL")
    add_if_set("plex_token", config.plex_token, "PLEX_TOKEN")
    if config.plex_enabled is not None:
        runtime_updates["plex_enabled"] = config.plex_enabled

    # Docker
    add_if_set("docker_host", config.docker_host, "DOCKER_HOST")
    if config.docker_enabled is not None:
        runtime_updates["docker_enabled"] = config.docker_enabled

    # Calendar
    add_if_set("google_credentials_path", config.google_credentials_path, "GOOGLE_CREDENTIALS_PATH")
    add_if_set("google_calendar_ids", config.google_calendar_ids, "GOOGLE_CALENDAR_IDS")
    if config.calendar_enabled is not None:
        runtime_updates["calendar_enabled"] = config.calendar_enabled

    # Weather
    if config.weather_latitude is not None:
        updates["WEATHER_LATITUDE"] = str(config.weather_latitude)
    if config.weather_longitude is not None:
        updates["WEATHER_LONGITUDE"] = str(config.weather_longitude)
    if config.weather_enabled is not None:
        runtime_updates["weather_enabled"] = config.weather_enabled

    # News
    add_if_set("news_api_key", config.news_api_key, "NEWS_API_KEY")
    add_if_set("news_country", config.news_country, "NEWS_COUNTRY")
    if config.news_enabled is not None:
        runtime_updates["news_enabled"] = config.news_enabled

    # Application
    if config.poll_interval is not None:
        updates["POLL_INTERVAL"] = str(config.poll_interval)
    if config.cache_ttl is not None:
        updates["CACHE_TTL"] = str(config.cache_ttl)
    add_if_set("cors_origins", config.cors_origins, "CORS_ORIGINS")

    # Save runtime config (enabled flags) - this always succeeds even if empty
    if runtime_updates:
        current_runtime = get_runtime_config()
        current_runtime.update(runtime_updates)
        runtime_success = save_runtime_config(current_runtime)
        if runtime_success:
            # Clear cache for affected services so changes take effect immediately
            await cache_service.clear()
        else:
            logger.warning("Failed to save runtime config, but continuing with .env save")

    if not updates and not runtime_updates:
        return {"status": "no_changes", "message": "No configuration values to update"}

    # Write credentials to .env (skip if no credential updates)
    env_success = True
    if updates:
        env_success = write_env(updates)

    if env_success:
        # Clear settings cache to reload
        get_settings.cache_clear()

        total_updates = len(updates) + len(runtime_updates)
        return {
            "status": "success",
            "message": f"Configuration saved ({total_updates} values updated)",
            "updated_keys": list(updates.keys()) + list(runtime_updates.keys()),
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to save configuration")


def _get_real_value(request_value: str, settings_value: str) -> str:
    """Get real value, falling back to settings if masked placeholder is provided."""
    if request_value == MASK_VALUE:
        return settings_value
    return request_value or ""


@router.post("/test/{service}", response_model=TestConnectionResult)
async def test_connection(service: str, request: TestConnectionRequest):
    """Test connection for a specific service."""
    settings = get_settings()

    if service == "unifi":
        return await test_unifi_connection(
            host=request.unifi_host or "",
            username=request.unifi_username or "",
            password=_get_real_value(request.unifi_password or "", settings.unifi_password),
            site=request.unifi_site or "default",
            verify_ssl=request.unifi_verify_ssl or False,
        )

    elif service == "proxmox":
        return await test_proxmox_connection(
            host=request.proxmox_host or "",
            user=request.proxmox_user or "",
            token_name=request.proxmox_token_name or "",
            token_value=_get_real_value(request.proxmox_token_value or "", settings.proxmox_token_value),
            node=request.proxmox_node or "pve",
            verify_ssl=request.proxmox_verify_ssl or False,
        )

    elif service == "plex":
        return await test_plex_connection(
            url=request.plex_url or "",
            token=_get_real_value(request.plex_token or "", settings.plex_token),
        )

    elif service == "docker":
        return await test_docker_connection(
            host=request.docker_host,
        )

    elif service == "calendar":
        return await test_calendar_connection(
            credentials_path=request.google_credentials_path or "",
        )

    elif service == "weather":
        return await test_weather_connection(
            latitude=request.weather_latitude or 0.0,
            longitude=request.weather_longitude or 0.0,
        )

    elif service == "news":
        return await test_news_connection(
            api_key=_get_real_value(request.news_api_key or "", settings.news_api_key),
        )

    else:
        raise HTTPException(status_code=404, detail=f"Unknown service: {service}")
