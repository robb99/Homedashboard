import httpx
from datetime import datetime
import logging

from app.config import get_settings
from app.models.schemas import (
    ProxmoxStatus,
    ProxmoxNode,
    ProxmoxContainer,
    StatusLevel,
)
from app.services.cache import cache_service
from app.utils.runtime_config import get_service_enabled

logger = logging.getLogger(__name__)

CACHE_KEY = "proxmox_status"


class ProxmoxService:
    def __init__(self):
        pass

    def _get_auth_header(self, settings) -> dict:
        """Get API token authentication header."""
        return {
            "Authorization": f"PVEAPIToken={settings.proxmox_user}!{settings.proxmox_token_name}={settings.proxmox_token_value}"
        }

    async def get_status(self, use_cache: bool = True) -> ProxmoxStatus:
        """Get Proxmox cluster status."""
        # Check if service is disabled (from runtime config)
        if not get_service_enabled("proxmox"):
            return ProxmoxStatus(
                status=StatusLevel.UNKNOWN,
                error_message="Service disabled",
                last_updated=datetime.now(),
            )

        settings = get_settings()

        if use_cache:
            cached = await cache_service.get(CACHE_KEY)
            if cached:
                return cached

        if not settings.proxmox_host:
            return ProxmoxStatus(
                status=StatusLevel.UNKNOWN,
                error_message="Proxmox not configured",
                last_updated=datetime.now(),
            )

        try:
            async with httpx.AsyncClient(
                verify=settings.proxmox_verify_ssl,
                timeout=10.0,
                headers=self._get_auth_header(settings),
            ) as client:
                base_url = f"{settings.proxmox_host}/api2/json"
                node = settings.proxmox_node

                # Get node status
                node_response = await client.get(f"{base_url}/nodes/{node}/status")
                node_data = node_response.json().get("data", {})

                cpu_usage = node_data.get("cpu", 0) * 100
                memory = node_data.get("memory", {})
                memory_used = memory.get("used", 0)
                memory_total = memory.get("total", 1)
                memory_usage = (memory_used / memory_total) * 100 if memory_total else 0

                proxmox_node = ProxmoxNode(
                    name=node,
                    status="online",
                    cpu_usage=round(cpu_usage, 1),
                    memory_usage=round(memory_usage, 1),
                    memory_total=memory_total,
                    uptime=node_data.get("uptime"),
                )

                # Get LXC containers
                lxc_response = await client.get(f"{base_url}/nodes/{node}/lxc")
                lxc_data = lxc_response.json().get("data", [])

                containers = []
                for lxc in lxc_data:
                    vmid = lxc.get("vmid")
                    # Get detailed status for each container
                    try:
                        detail_response = await client.get(
                            f"{base_url}/nodes/{node}/lxc/{vmid}/status/current"
                        )
                        detail = detail_response.json().get("data", {})

                        mem_used = detail.get("mem", 0)
                        mem_total = detail.get("maxmem", 1)
                        disk_used = detail.get("disk", 0)
                        disk_total = detail.get("maxdisk", 1)

                        container = ProxmoxContainer(
                            vmid=vmid,
                            name=lxc.get("name", f"CT {vmid}"),
                            status=lxc.get("status", "unknown"),
                            type="lxc",
                            cpu_usage=round(detail.get("cpu", 0) * 100, 1),
                            memory_usage=round((mem_used / mem_total) * 100, 1) if mem_total else 0,
                            memory_total=mem_total,
                            disk_usage=round((disk_used / disk_total) * 100, 1) if disk_total else 0,
                            uptime=detail.get("uptime"),
                        )
                        containers.append(container)
                    except Exception as e:
                        logger.warning(f"Error getting LXC {vmid} details: {e}")
                        containers.append(
                            ProxmoxContainer(
                                vmid=vmid,
                                name=lxc.get("name", f"CT {vmid}"),
                                status=lxc.get("status", "unknown"),
                                type="lxc",
                            )
                        )

                # Get VMs
                qemu_response = await client.get(f"{base_url}/nodes/{node}/qemu")
                qemu_data = qemu_response.json().get("data", [])

                vms = []
                for vm in qemu_data:
                    vmid = vm.get("vmid")
                    try:
                        detail_response = await client.get(
                            f"{base_url}/nodes/{node}/qemu/{vmid}/status/current"
                        )
                        detail = detail_response.json().get("data", {})

                        mem_used = detail.get("mem", 0)
                        mem_total = detail.get("maxmem", 1)
                        disk_used = detail.get("disk", 0)
                        disk_total = detail.get("maxdisk", 1)

                        vm_obj = ProxmoxContainer(
                            vmid=vmid,
                            name=vm.get("name", f"VM {vmid}"),
                            status=vm.get("status", "unknown"),
                            type="qemu",
                            cpu_usage=round(detail.get("cpu", 0) * 100, 1),
                            memory_usage=round((mem_used / mem_total) * 100, 1) if mem_total else 0,
                            memory_total=mem_total,
                            disk_usage=round((disk_used / disk_total) * 100, 1) if disk_total else 0,
                            uptime=detail.get("uptime"),
                        )
                        vms.append(vm_obj)
                    except Exception as e:
                        logger.warning(f"Error getting VM {vmid} details: {e}")
                        vms.append(
                            ProxmoxContainer(
                                vmid=vmid,
                                name=vm.get("name", f"VM {vmid}"),
                                status=vm.get("status", "unknown"),
                                type="qemu",
                            )
                        )

                all_items = containers + vms
                total_running = sum(1 for i in all_items if i.status == "running")
                total_stopped = sum(1 for i in all_items if i.status == "stopped")

                # Determine status
                if total_stopped > 0 and total_running > 0:
                    status = StatusLevel.WARNING
                elif total_running > 0:
                    status = StatusLevel.HEALTHY
                else:
                    status = StatusLevel.WARNING

                result = ProxmoxStatus(
                    status=status,
                    node=proxmox_node,
                    containers=containers,
                    vms=vms,
                    total_running=total_running,
                    total_stopped=total_stopped,
                    last_updated=datetime.now(),
                )

                await cache_service.set(CACHE_KEY, result)
                return result

        except Exception as e:
            logger.error(f"Proxmox error: {e}")
            return ProxmoxStatus(
                status=StatusLevel.ERROR,
                error_message=str(e),
                last_updated=datetime.now(),
            )


proxmox_service = ProxmoxService()
