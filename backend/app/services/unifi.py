import httpx
from datetime import datetime
from typing import Optional
import logging

from app.config import get_settings
from app.models.schemas import UnifiStatus, UnifiDevice, UnifiClient, StatusLevel
from app.services.cache import cache_service

logger = logging.getLogger(__name__)

CACHE_KEY = "unifi_status"


class UnifiService:
    def __init__(self):
        self.settings = get_settings()
        self._cookies: Optional[dict] = None

    async def _login(self, client: httpx.AsyncClient) -> bool:
        """Authenticate with Unifi Controller."""
        try:
            login_url = f"{self.settings.unifi_host}/api/auth/login"
            response = await client.post(
                login_url,
                json={
                    "username": self.settings.unifi_username,
                    "password": self.settings.unifi_password,
                },
            )
            if response.status_code == 200:
                self._cookies = dict(response.cookies)
                return True
            logger.error(f"Unifi login failed: {response.status_code}")
            return False
        except Exception as e:
            logger.error(f"Unifi login error: {e}")
            return False

    async def get_status(self, use_cache: bool = True) -> UnifiStatus:
        """Get Unifi controller status."""
        if use_cache:
            cached = await cache_service.get(CACHE_KEY)
            if cached:
                return cached

        if not self.settings.unifi_host:
            return UnifiStatus(
                status=StatusLevel.UNKNOWN,
                error_message="Unifi not configured",
                last_updated=datetime.now(),
            )

        try:
            async with httpx.AsyncClient(
                verify=self.settings.unifi_verify_ssl,
                timeout=10.0,
            ) as client:
                if not await self._login(client):
                    return UnifiStatus(
                        status=StatusLevel.ERROR,
                        error_message="Authentication failed",
                        last_updated=datetime.now(),
                    )

                # Get devices
                devices_url = f"{self.settings.unifi_host}/proxy/network/api/s/{self.settings.unifi_site}/stat/device"
                devices_response = await client.get(devices_url, cookies=self._cookies)
                devices_data = devices_response.json().get("data", [])

                devices = []
                devices_online = 0
                devices_offline = 0

                for d in devices_data:
                    device = UnifiDevice(
                        name=d.get("name", d.get("mac", "Unknown")),
                        mac=d.get("mac", ""),
                        model=d.get("model", "Unknown"),
                        ip=d.get("ip"),
                        status="online" if d.get("state", 0) == 1 else "offline",
                        uptime=d.get("uptime"),
                        type=d.get("type", "unknown"),
                    )
                    devices.append(device)
                    if device.status == "online":
                        devices_online += 1
                    else:
                        devices_offline += 1

                # Get clients
                clients_url = f"{self.settings.unifi_host}/proxy/network/api/s/{self.settings.unifi_site}/stat/sta"
                clients_response = await client.get(clients_url, cookies=self._cookies)
                clients_data = clients_response.json().get("data", [])

                clients = []
                for c in clients_data:
                    client_obj = UnifiClient(
                        hostname=c.get("hostname") or c.get("name"),
                        mac=c.get("mac", ""),
                        ip=c.get("ip"),
                        network=c.get("network"),
                        is_wired=c.get("is_wired", False),
                    )
                    clients.append(client_obj)

                # Determine overall status
                if devices_offline > 0:
                    status = StatusLevel.WARNING
                elif devices_online > 0:
                    status = StatusLevel.HEALTHY
                else:
                    status = StatusLevel.UNKNOWN

                result = UnifiStatus(
                    status=status,
                    devices=devices,
                    clients=clients,
                    device_count=len(devices),
                    client_count=len(clients),
                    devices_online=devices_online,
                    devices_offline=devices_offline,
                    last_updated=datetime.now(),
                )

                await cache_service.set(CACHE_KEY, result)
                return result

        except Exception as e:
            logger.error(f"Unifi error: {e}")
            return UnifiStatus(
                status=StatusLevel.ERROR,
                error_message=str(e),
                last_updated=datetime.now(),
            )


unifi_service = UnifiService()
