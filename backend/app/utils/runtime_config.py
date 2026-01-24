"""
Runtime configuration manager for service enabled/disabled flags.
Stores configuration in a JSON file that can be updated without container restart.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Path to runtime config file (in mounted volume)
RUNTIME_CONFIG_PATH = Path("/app/config/runtime_config.json")

# Default values for all enabled flags
DEFAULT_CONFIG = {
    "unifi_enabled": True,
    "proxmox_enabled": True,
    "plex_enabled": True,
    "docker_enabled": True,
    "calendar_enabled": True,
    "weather_enabled": True,
    "news_enabled": True,
    "unraid_enabled": True,
}


def get_runtime_config() -> Dict[str, Any]:
    """
    Read runtime configuration from JSON file.
    Returns default config if file doesn't exist or is invalid.
    """
    if not RUNTIME_CONFIG_PATH.exists():
        logger.debug("Runtime config file not found, using defaults")
        return DEFAULT_CONFIG.copy()

    try:
        with open(RUNTIME_CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
            # Merge with defaults to ensure all keys exist
            result = DEFAULT_CONFIG.copy()
            result.update(config)
            return result
    except Exception as e:
        logger.error(f"Error reading runtime config: {e}")
        return DEFAULT_CONFIG.copy()


def save_runtime_config(config: Dict[str, Any]) -> bool:
    """
    Save runtime configuration to JSON file.
    Only saves enabled flags, not credentials.

    Args:
        config: Dictionary containing enabled flags

    Returns:
        True if successful, False otherwise
    """
    # Filter to only save enabled flags
    enabled_keys = [k for k in DEFAULT_CONFIG.keys()]
    filtered_config = {k: v for k, v in config.items() if k in enabled_keys}

    # Ensure directory exists
    try:
        RUNTIME_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create config directory: {e}")
        return False

    try:
        with open(RUNTIME_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(filtered_config, f, indent=2)
        logger.info(f"Saved runtime config: {filtered_config}")
        return True
    except Exception as e:
        logger.error(f"Failed to save runtime config: {e}")
        return False


def get_service_enabled(service: str) -> bool:
    """
    Check if a specific service is enabled.

    Args:
        service: Service name (e.g., 'unifi', 'proxmox')

    Returns:
        True if enabled, False otherwise
    """
    config = get_runtime_config()
    key = f"{service}_enabled"
    return config.get(key, True)


def set_service_enabled(service: str, enabled: bool) -> bool:
    """
    Set a specific service's enabled status.

    Args:
        service: Service name (e.g., 'unifi', 'proxmox')
        enabled: Whether the service should be enabled

    Returns:
        True if successful, False otherwise
    """
    config = get_runtime_config()
    key = f"{service}_enabled"
    config[key] = enabled
    return save_runtime_config(config)
