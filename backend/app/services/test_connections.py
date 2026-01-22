"""
Connection testing service for setup wizard.
Provides lightweight connection tests for all services without caching.
"""
import httpx
import docker
import os
import logging
from typing import Optional

from app.models.schemas import TestConnectionResult

logger = logging.getLogger(__name__)


async def test_unifi_connection(
    host: str,
    username: str,
    password: str,
    site: str = "default",
    verify_ssl: bool = False,
) -> TestConnectionResult:
    """Test UniFi controller connection with login attempt."""
    if not host or not username or not password:
        return TestConnectionResult(
            success=False,
            message="Missing required fields",
            details="Host, username, and password are required",
        )

    try:
        async with httpx.AsyncClient(verify=verify_ssl, timeout=10.0) as client:
            login_url = f"{host}/api/auth/login"
            response = await client.post(
                login_url,
                json={"username": username, "password": password},
            )

            if response.status_code == 200:
                return TestConnectionResult(
                    success=True,
                    message="Successfully connected to UniFi controller",
                    details=f"Site: {site}",
                )
            elif response.status_code == 401:
                return TestConnectionResult(
                    success=False,
                    message="Authentication failed",
                    details="Invalid username or password",
                )
            else:
                return TestConnectionResult(
                    success=False,
                    message=f"Connection failed with status {response.status_code}",
                    details=response.text[:200] if response.text else None,
                )

    except httpx.ConnectError:
        return TestConnectionResult(
            success=False,
            message="Connection failed",
            details=f"Could not connect to {host}. Check the host URL.",
        )
    except Exception as e:
        return TestConnectionResult(
            success=False,
            message="Connection error",
            details=str(e),
        )


async def test_proxmox_connection(
    host: str,
    user: str,
    token_name: str,
    token_value: str,
    node: str = "pve",
    verify_ssl: bool = False,
) -> TestConnectionResult:
    """Test Proxmox connection with API version check."""
    if not host or not user or not token_name or not token_value:
        return TestConnectionResult(
            success=False,
            message="Missing required fields",
            details="Host, user, token name, and token value are required",
        )

    try:
        auth_header = f"PVEAPIToken={user}!{token_name}={token_value}"

        async with httpx.AsyncClient(
            verify=verify_ssl,
            timeout=10.0,
            headers={"Authorization": auth_header},
        ) as client:
            # Test with version endpoint (lightweight)
            version_url = f"{host}/api2/json/version"
            response = await client.get(version_url)

            if response.status_code == 200:
                data = response.json().get("data", {})
                version = data.get("version", "unknown")
                return TestConnectionResult(
                    success=True,
                    message="Successfully connected to Proxmox",
                    details=f"Version: {version}, Node: {node}",
                )
            elif response.status_code == 401:
                return TestConnectionResult(
                    success=False,
                    message="Authentication failed",
                    details="Invalid API token credentials",
                )
            else:
                return TestConnectionResult(
                    success=False,
                    message=f"Connection failed with status {response.status_code}",
                    details=response.text[:200] if response.text else None,
                )

    except httpx.ConnectError:
        return TestConnectionResult(
            success=False,
            message="Connection failed",
            details=f"Could not connect to {host}. Check the host URL.",
        )
    except Exception as e:
        return TestConnectionResult(
            success=False,
            message="Connection error",
            details=str(e),
        )


async def test_plex_connection(
    url: str,
    token: str,
) -> TestConnectionResult:
    """Test Plex connection with identity endpoint."""
    if not url or not token:
        return TestConnectionResult(
            success=False,
            message="Missing required fields",
            details="URL and token are required",
        )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {
                "X-Plex-Token": token,
                "Accept": "application/json",
            }

            # Test with identity endpoint (lightweight)
            identity_url = f"{url}/identity"
            response = await client.get(identity_url, headers=headers)

            if response.status_code == 200:
                data = response.json().get("MediaContainer", {})
                machine_id = data.get("machineIdentifier", "unknown")[:8]
                return TestConnectionResult(
                    success=True,
                    message="Successfully connected to Plex",
                    details=f"Server ID: {machine_id}...",
                )
            elif response.status_code == 401:
                return TestConnectionResult(
                    success=False,
                    message="Authentication failed",
                    details="Invalid Plex token",
                )
            else:
                return TestConnectionResult(
                    success=False,
                    message=f"Connection failed with status {response.status_code}",
                    details=response.text[:200] if response.text else None,
                )

    except httpx.ConnectError:
        return TestConnectionResult(
            success=False,
            message="Connection failed",
            details=f"Could not connect to {url}. Check the URL.",
        )
    except Exception as e:
        return TestConnectionResult(
            success=False,
            message="Connection error",
            details=str(e),
        )


async def test_docker_connection(
    host: Optional[str] = None,
) -> TestConnectionResult:
    """Test Docker connection with docker info."""
    try:
        if host:
            client = docker.DockerClient(base_url=host)
        else:
            client = docker.from_env()

        info = client.info()
        containers = info.get("Containers", 0)
        images = info.get("Images", 0)

        return TestConnectionResult(
            success=True,
            message="Successfully connected to Docker",
            details=f"Containers: {containers}, Images: {images}",
        )

    except docker.errors.DockerException as e:
        return TestConnectionResult(
            success=False,
            message="Docker connection failed",
            details=str(e),
        )
    except Exception as e:
        return TestConnectionResult(
            success=False,
            message="Connection error",
            details=str(e),
        )


async def test_calendar_connection(
    credentials_path: str,
) -> TestConnectionResult:
    """Test Google Calendar connection by checking credentials file."""
    if not credentials_path:
        return TestConnectionResult(
            success=False,
            message="Missing credentials path",
            details="Google credentials file path is required",
        )

    if not os.path.exists(credentials_path):
        return TestConnectionResult(
            success=False,
            message="Credentials file not found",
            details=f"File does not exist: {credentials_path}",
        )

    try:
        with open(credentials_path, "r") as f:
            content = f.read()
            if "service_account" in content or "client_id" in content:
                return TestConnectionResult(
                    success=True,
                    message="Credentials file found and valid",
                    details="File contains valid Google credentials structure",
                )
            else:
                return TestConnectionResult(
                    success=False,
                    message="Invalid credentials file",
                    details="File does not appear to be a valid Google credentials file",
                )
    except Exception as e:
        return TestConnectionResult(
            success=False,
            message="Error reading credentials file",
            details=str(e),
        )


async def test_weather_connection(
    latitude: float,
    longitude: float,
) -> TestConnectionResult:
    """Test Open-Meteo connection with coordinates."""
    if latitude == 0.0 and longitude == 0.0:
        return TestConnectionResult(
            success=False,
            message="Invalid coordinates",
            details="Please provide valid latitude and longitude",
        )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current_weather": "true",
            }

            response = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params=params,
            )

            if response.status_code == 200:
                data = response.json()
                current = data.get("current_weather", {})
                temp = current.get("temperature", "N/A")
                return TestConnectionResult(
                    success=True,
                    message="Successfully connected to Open-Meteo",
                    details=f"Current temperature: {temp}C at ({latitude}, {longitude})",
                )
            else:
                return TestConnectionResult(
                    success=False,
                    message=f"API returned status {response.status_code}",
                    details=response.text[:200] if response.text else None,
                )

    except Exception as e:
        return TestConnectionResult(
            success=False,
            message="Connection error",
            details=str(e),
        )


async def test_news_connection(
    api_key: str,
) -> TestConnectionResult:
    """Test NewsAPI connection with key validation."""
    if not api_key:
        return TestConnectionResult(
            success=False,
            message="Missing API key",
            details="NewsAPI key is required",
        )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            params = {
                "apiKey": api_key,
                "country": "us",
                "pageSize": 1,
            }

            response = await client.get(
                "https://newsapi.org/v2/top-headlines",
                params=params,
            )

            data = response.json()

            if response.status_code == 200 and data.get("status") == "ok":
                total = data.get("totalResults", 0)
                return TestConnectionResult(
                    success=True,
                    message="Successfully connected to NewsAPI",
                    details=f"API key valid, {total} articles available",
                )
            elif response.status_code == 401:
                return TestConnectionResult(
                    success=False,
                    message="Invalid API key",
                    details=data.get("message", "Authentication failed"),
                )
            else:
                return TestConnectionResult(
                    success=False,
                    message=f"API error: {data.get('code', 'unknown')}",
                    details=data.get("message", response.text[:200]),
                )

    except Exception as e:
        return TestConnectionResult(
            success=False,
            message="Connection error",
            details=str(e),
        )
