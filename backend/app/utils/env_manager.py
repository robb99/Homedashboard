"""
Environment file management utilities.
Provides safe read/write operations for .env files with backup support.
"""
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Path to .env file (project root)
ENV_FILE_PATH = Path(__file__).parent.parent.parent.parent / ".env"


def read_env() -> Dict[str, str]:
    """
    Parse .env file and return key-value pairs.
    Preserves empty values and handles quoted strings.
    """
    env_vars: Dict[str, str] = {}

    if not ENV_FILE_PATH.exists():
        return env_vars

    try:
        with open(ENV_FILE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Split on first = only
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip()

                    # Remove surrounding quotes if present
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]

                    env_vars[key] = value
    except Exception as e:
        logger.error(f"Error reading .env file: {e}")

    return env_vars


def backup_env() -> Optional[str]:
    """
    Create a timestamped backup of the .env file.
    Returns the backup file path or None if no backup was created.
    """
    if not ENV_FILE_PATH.exists():
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = ENV_FILE_PATH.parent / f".env.backup.{timestamp}"

    try:
        shutil.copy2(ENV_FILE_PATH, backup_path)
        logger.info(f"Created .env backup: {backup_path}")
        return str(backup_path)
    except Exception as e:
        logger.error(f"Failed to create .env backup: {e}")
        return None


def write_env(updates: Dict[str, str]) -> bool:
    """
    Update .env file with new values using atomic write.
    Preserves existing values and comments, only updates specified keys.

    Args:
        updates: Dictionary of key-value pairs to update

    Returns:
        True if successful, False otherwise
    """
    # Create backup before writing
    backup_env()

    # Read existing content to preserve comments and order
    existing_lines = []
    existing_keys = set()

    if ENV_FILE_PATH.exists():
        try:
            with open(ENV_FILE_PATH, "r", encoding="utf-8") as f:
                existing_lines = f.readlines()
        except Exception as e:
            logger.error(f"Error reading existing .env: {e}")
            existing_lines = []

    # Build new content
    new_lines = []

    for line in existing_lines:
        stripped = line.strip()

        # Preserve comments and empty lines
        if not stripped or stripped.startswith("#"):
            new_lines.append(line)
            continue

        # Check if this line has a key we're updating
        if "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            existing_keys.add(key)

            if key in updates:
                # Update the value
                value = updates[key]
                # Quote values with spaces
                if " " in value and not (value.startswith('"') or value.startswith("'")):
                    value = f'"{value}"'
                new_lines.append(f"{key}={value}\n")
            else:
                # Keep original line
                new_lines.append(line)
        else:
            new_lines.append(line)

    # Add new keys that weren't in the original file
    for key, value in updates.items():
        if key not in existing_keys:
            # Quote values with spaces
            if " " in value and not (value.startswith('"') or value.startswith("'")):
                value = f'"{value}"'
            new_lines.append(f"{key}={value}\n")

    # Atomic write: write to temp file then rename
    temp_path = ENV_FILE_PATH.parent / ".env.tmp"

    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        # Atomic rename
        os.replace(temp_path, ENV_FILE_PATH)
        logger.info(f"Successfully updated .env with {len(updates)} changes")
        return True

    except Exception as e:
        logger.error(f"Failed to write .env: {e}")
        # Clean up temp file if it exists
        if temp_path.exists():
            temp_path.unlink()
        return False


def get_env_path() -> Path:
    """Return the path to the .env file."""
    return ENV_FILE_PATH
