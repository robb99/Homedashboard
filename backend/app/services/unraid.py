import httpx
import re
from datetime import datetime
from typing import Optional
import logging

from app.config import get_settings
from app.models.schemas import (
    UnraidStatus,
    UnraidArray,
    UnraidDisk,
    UnraidContainer,
    UnraidVM,
    UnraidSystem,
    StatusLevel,
)
from app.services.cache import cache_service
from app.utils.runtime_config import get_service_enabled

logger = logging.getLogger(__name__)

CACHE_KEY = "unraid_status"


class UnraidService:
    def __init__(self):
        self._cookies: Optional[dict] = None
        self._csrf_token: Optional[str] = None

    async def _login(self, client: httpx.AsyncClient, settings) -> bool:
        """Authenticate with Unraid server."""
        try:
            # First, get the login page to obtain any CSRF token
            login_page_url = f"{settings.unraid_host}/login"
            page_response = await client.get(login_page_url)

            # Extract CSRF token if present (Unraid may use csrf_token in form)
            csrf_token = None
            if page_response.status_code == 200:
                content = page_response.text
                # Look for csrf_token in the page
                import re
                csrf_match = re.search(r'name=["\']csrf_token["\']\s+value=["\']([^"\']+)["\']', content)
                if csrf_match:
                    csrf_token = csrf_match.group(1)

            # Build login data
            login_data = {
                "username": settings.unraid_username,
                "password": settings.unraid_password,
            }
            if csrf_token:
                login_data["csrf_token"] = csrf_token

            # Perform login
            response = await client.post(
                login_page_url,
                data=login_data,
                follow_redirects=True,
            )

            # Unraid returns a redirect on successful login
            # Check for session cookie
            all_cookies = dict(client.cookies)
            if response.status_code in (200, 302) and all_cookies:
                self._cookies = all_cookies

                # Extract CSRF token from cookies first
                self._csrf_token = (
                    all_cookies.get("csrf_token") or
                    all_cookies.get("_csrf") or
                    all_cookies.get("XSRF-TOKEN") or
                    ""
                )

                # Check response headers for CSRF token
                if not self._csrf_token:
                    self._csrf_token = response.headers.get("x-csrf-token", "")
                if not self._csrf_token:
                    self._csrf_token = response.headers.get("csrf-token", "")

                # Try to extract from HTML
                if not self._csrf_token:
                    html = response.text
                    # Look for meta tag
                    meta_match = re.search(r'<meta[^>]+name=["\']csrf-token["\'][^>]+content=["\']([^"\']+)["\']', html)
                    if meta_match:
                        self._csrf_token = meta_match.group(1)
                    else:
                        # Look for hidden input
                        input_match = re.search(r'<input[^>]+name=["\'](?:csrf_token|_csrf|csrfmiddlewaretoken)["\'][^>]+value=["\']([^"\']+)["\']', html)
                        if input_match:
                            self._csrf_token = input_match.group(1)
                        else:
                            # Try var csrf_token = "..."
                            var_match = re.search(r'var\s+csrf_token\s*=\s*["\']([^"\']+)["\']', html)
                            if var_match:
                                self._csrf_token = var_match.group(1)

                logger.info(f"Unraid login successful, CSRF token found: {bool(self._csrf_token)}")
                return True

            logger.error(f"Unraid login failed: {response.status_code}, cookies: {list(all_cookies.keys())}")
            return False
        except Exception as e:
            logger.error(f"Unraid login error: {e}")
            return False

    async def _graphql_query(
        self, client: httpx.AsyncClient, settings, query: str, variables: dict = None
    ) -> Optional[dict]:
        """Execute a GraphQL query against Unraid API."""
        try:
            graphql_url = f"{settings.unraid_host}/graphql"
            payload = {"query": query}
            if variables:
                payload["variables"] = variables

            # Include CSRF token in headers
            headers = {}
            if self._csrf_token:
                headers["x-csrf-token"] = self._csrf_token

            response = await client.post(
                graphql_url,
                json=payload,
                cookies=self._cookies,
                headers=headers,
            )

            if response.status_code == 200:
                data = response.json()
                if "errors" in data:
                    logger.error(f"Unraid GraphQL errors: {data['errors']}")
                    # Still return data if partial results exist
                    if data.get("data"):
                        return data.get("data")
                    return None
                return data.get("data")
            else:
                # Log the response body for debugging
                try:
                    error_body = response.text[:500]
                    logger.error(f"Unraid GraphQL request failed: {response.status_code}, body: {error_body}")
                except:
                    logger.error(f"Unraid GraphQL request failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Unraid GraphQL error: {e}")
            return None

    async def get_status(self, use_cache: bool = True) -> UnraidStatus:
        """Get Unraid server status."""
        # Check if service is disabled (from runtime config)
        if not get_service_enabled("unraid"):
            return UnraidStatus(
                status=StatusLevel.UNKNOWN,
                error_message="Service disabled",
                last_updated=datetime.now(),
            )

        settings = get_settings()

        if use_cache:
            cached = await cache_service.get(CACHE_KEY)
            if cached:
                return cached

        if not settings.unraid_host:
            return UnraidStatus(
                status=StatusLevel.UNKNOWN,
                error_message="Unraid not configured",
                last_updated=datetime.now(),
            )

        try:
            async with httpx.AsyncClient(
                verify=settings.unraid_verify_ssl,
                timeout=15.0,
            ) as client:
                if not await self._login(client, settings):
                    return UnraidStatus(
                        status=StatusLevel.ERROR,
                        error_message="Authentication failed",
                        last_updated=datetime.now(),
                    )

                # Fetch all data using GraphQL queries
                array_data = await self._fetch_array_status(client, settings)
                docker_data = await self._fetch_docker_containers(client, settings)
                vm_data = await self._fetch_vms(client, settings)
                system_data = await self._fetch_system_info(client, settings)

                # Build response
                array = None
                containers = []
                vms = []
                system = None
                container_running = 0
                vm_running = 0

                # Process array data
                if array_data:
                    array = self._parse_array_data(array_data)

                # Process containers
                if docker_data:
                    containers = self._parse_docker_data(docker_data)
                    container_running = sum(1 for c in containers if c.status.lower() == "running")

                # Process VMs
                if vm_data:
                    vms = self._parse_vm_data(vm_data)
                    vm_running = sum(1 for v in vms if v.status.lower() == "running")

                # Process system info
                if system_data:
                    system = self._parse_system_data(system_data)

                # Determine overall status
                status = self._determine_status(array, containers, vms, system)

                result = UnraidStatus(
                    status=status,
                    array=array,
                    containers=containers,
                    vms=vms,
                    system=system,
                    container_count=len(containers),
                    container_running=container_running,
                    vm_count=len(vms),
                    vm_running=vm_running,
                    last_updated=datetime.now(),
                )

                await cache_service.set(CACHE_KEY, result)
                return result

        except Exception as e:
            logger.error(f"Unraid error: {e}")
            return UnraidStatus(
                status=StatusLevel.ERROR,
                error_message=str(e),
                last_updated=datetime.now(),
            )

    async def _fetch_array_status(self, client: httpx.AsyncClient, settings) -> Optional[dict]:
        """Fetch array status from Unraid GraphQL API."""
        # Unraid 7.2+ - expanded query with parity, disk health, and temperature
        query = """
        query {
            array {
                state
                capacity {
                    kilobytes {
                        total
                        used
                        free
                    }
                }
                parities {
                    name
                    size
                    status
                    temp
                    numErrors
                }
            }
            disks {
                name
                device
                size
                type
                status
                temp
                smartStatus
                numErrors
            }
        }
        """
        return await self._graphql_query(client, settings, query)

    async def _fetch_docker_containers(self, client: httpx.AsyncClient, settings) -> Optional[dict]:
        """Fetch Docker container info from Unraid GraphQL API."""
        # Unraid 7.x uses 'docker { containers }' and 'names' (not 'name')
        query = """
        query {
            docker {
                containers {
                    names
                    state
                    image
                }
            }
        }
        """
        return await self._graphql_query(client, settings, query)

    async def _fetch_vms(self, client: httpx.AsyncClient, settings) -> Optional[dict]:
        """Fetch VM info from Unraid GraphQL API."""
        # Unraid 7.x: vms is a wrapper type, try to find nested structure
        # Try 'domains' as VMs are libvirt domains
        query = """
        query {
            vms {
                domain {
                    name
                    state
                }
            }
        }
        """
        result = await self._graphql_query(client, settings, query)
        if result:
            return result

        # Fallback: try 'domains' plural
        fallback_query = """
        query {
            vms {
                domains {
                    name
                    state
                }
            }
        }
        """
        return await self._graphql_query(client, settings, fallback_query)

    async def _fetch_system_info(self, client: httpx.AsyncClient, settings) -> Optional[dict]:
        """Fetch system info from Unraid GraphQL API."""
        # Unraid 7.2+ - expanded query with CPU, memory, and uptime
        query = """
        query {
            vars {
                version
                regTy
            }
            info {
                cpu {
                    threads
                    temperature
                }
                memory {
                    total
                    used
                    free
                    available
                }
                os {
                    uptime
                }
            }
        }
        """
        result = await self._graphql_query(client, settings, query)
        if result:
            return result

        # Fallback to just version and uptime if expanded fields not available
        fallback_query = """
        query {
            vars {
                version
            }
            info {
                os {
                    uptime
                }
            }
        }
        """
        return await self._graphql_query(client, settings, fallback_query)

    def _parse_array_data(self, data: dict) -> UnraidArray:
        """Parse array data from GraphQL response."""
        array_info = data.get("array", {}) or {}
        capacity = array_info.get("capacity", {}) or {}
        # Unraid 7.x uses capacity { kilobytes { total, used, free } }
        disk_capacity = capacity.get("kilobytes", {}) or capacity.get("disks", {}) or {}

        disks = []
        for disk in data.get("disks", []) or []:
            # Use 'color' field as status indicator if 'status' not available
            # Unraid disk colors: green=healthy, yellow=warning, red=error, blue=parity
            disk_status = disk.get("status") or disk.get("color") or "unknown"

            # Parse SMART status - normalize to lowercase for consistency
            smart_status_raw = disk.get("smartStatus") or "unknown"
            smart_status = str(smart_status_raw).lower() if smart_status_raw else "unknown"

            # Parse num errors
            num_errors = disk.get("numErrors") or 0
            if isinstance(num_errors, str):
                try:
                    num_errors = int(num_errors)
                except:
                    num_errors = 0

            disks.append(UnraidDisk(
                name=disk.get("name", "Unknown"),
                device=disk.get("device", ""),
                size=disk.get("size", 0) or 0,
                status=disk_status,
                temp=disk.get("temp"),
                smart_status=smart_status,
                num_errors=num_errors,
            ))

        # Parse parity info from array.parities if available (Unraid 7.2+)
        parities = array_info.get("parities", []) or []
        parity_status = "unknown"
        parity_progress = None
        parity_errors = 0

        if parities:
            # Aggregate parity status from all parity disks
            parity_statuses = []
            for parity in parities:
                p_status = (parity.get("status") or "").lower()
                if p_status:
                    parity_statuses.append(p_status)
                # Sum up parity errors
                p_errors = parity.get("numErrors") or 0
                if isinstance(p_errors, str):
                    try:
                        p_errors = int(p_errors)
                    except:
                        p_errors = 0
                parity_errors += p_errors

            # Determine overall parity status
            # Priority: invalid/degraded > syncing/checking > valid
            if any(s in ["invalid", "degraded", "failed"] for s in parity_statuses):
                parity_status = "invalid"
            elif any(s in ["syncing", "checking", "rebuilding"] for s in parity_statuses):
                parity_status = "syncing"
            elif any(s in ["valid", "ok", "passed"] for s in parity_statuses):
                parity_status = "valid"
            elif parity_statuses:
                parity_status = parity_statuses[0]  # Use first status if unknown type
        else:
            # Fallback: default to "valid" if array is started
            array_state = (array_info.get("state") or "").lower()
            parity_status = "valid" if array_state == "started" else "unknown"

        # Convert from kilobytes to bytes for proper display
        # Unraid uses decimal KB (1000 bytes), not binary KiB (1024 bytes)
        # Ensure values are integers (GraphQL may return strings)
        total_kb = disk_capacity.get("total", 0) or 0
        used_kb = disk_capacity.get("used", 0) or 0
        free_kb = disk_capacity.get("free", 0) or 0

        # Convert to int if string
        if isinstance(total_kb, str):
            total_kb = int(total_kb)
        if isinstance(used_kb, str):
            used_kb = int(used_kb)
        if isinstance(free_kb, str):
            free_kb = int(free_kb)

        # Convert from decimal KB to bytes (KB = 1000 bytes in Unraid)
        total = total_kb * 1000
        used = used_kb * 1000
        free = free_kb * 1000

        return UnraidArray(
            status=array_info.get("state", "unknown"),
            parity_status=parity_status,
            parity_progress=parity_progress,
            parity_errors=parity_errors,
            total_size=total,
            used_size=used,
            free_size=free,
            disks=disks,
        )

    def _parse_docker_data(self, data: dict) -> list:
        """Parse Docker container data from GraphQL response."""
        containers = []
        # Handle nested docker { containers { ... } } structure
        docker_data = data.get("docker", {}) or {}
        container_list = docker_data.get("containers", [])
        if not container_list:
            # Fallback to flat structure
            container_list = data.get("dockerContainers", []) or []
        for container in container_list:
            # Handle 'names' field (array) instead of 'name'
            name = container.get("names") or container.get("name", "Unknown")
            if isinstance(name, list):
                name = name[0].lstrip("/") if name else "Unknown"
            else:
                name = str(name).lstrip("/")
            containers.append(UnraidContainer(
                name=name,
                image=container.get("image", ""),
                status=container.get("state", "stopped"),
                uptime=container.get("status"),
            ))
        return containers

    def _parse_vm_data(self, data: dict) -> list:
        """Parse VM data from GraphQL response."""
        vms = []
        # Handle nested vms { domain/domains { ... } } structure
        vms_data = data.get("vms", {}) or {}
        if isinstance(vms_data, dict):
            vm_list = vms_data.get("domains", []) or vms_data.get("domain", []) or []
        else:
            vm_list = vms_data if isinstance(vms_data, list) else []
        if not isinstance(vm_list, list):
            vm_list = [vm_list] if vm_list else []
        for vm in vm_list:
            if vm:
                vms.append(UnraidVM(
                    name=vm.get("name", "Unknown"),
                    status=vm.get("state", "stopped"),
                    vcpus=vm.get("coreCount", 0) or vm.get("vcpus", 0) or 0,
                    memory=vm.get("ramAllocation", 0) or vm.get("memory", 0) or 0,
                ))
        return vms

    def _parse_system_data(self, data: dict) -> UnraidSystem:
        """Parse system info from GraphQL response."""
        vars_info = data.get("vars", {}) or {}
        info_data = data.get("info", {}) or {}
        os_info = info_data.get("os", {}) or {}
        cpu_info = info_data.get("cpu", {}) or {}
        memory_info = info_data.get("memory", {}) or {}

        # Parse uptime - try info.os.uptime first
        uptime = os_info.get("uptime") or vars_info.get("uptime") or 0
        if isinstance(uptime, str):
            try:
                uptime = int(uptime)
            except:
                uptime = 0

        # Parse CPU temperature (Unraid 7.2+)
        cpu_temp = cpu_info.get("temperature")
        if cpu_temp is not None:
            if isinstance(cpu_temp, str):
                try:
                    cpu_temp = int(float(cpu_temp))
                except:
                    cpu_temp = None

        # Parse memory metrics (Unraid 7.2+)
        # Memory values are typically in bytes or KB from the API
        memory_total = memory_info.get("total") or 0
        memory_used = memory_info.get("used") or 0

        # Convert to int if string
        if isinstance(memory_total, str):
            try:
                memory_total = int(memory_total)
            except:
                memory_total = 0
        if isinstance(memory_used, str):
            try:
                memory_used = int(memory_used)
            except:
                memory_used = 0

        # Calculate memory percentage
        memory_percent = 0.0
        if memory_total > 0:
            memory_percent = (memory_used / memory_total) * 100

        # CPU usage not directly available from GraphQL
        # Could potentially calculate from /proc/stat in future
        cpu_usage = 0.0

        return UnraidSystem(
            cpu_usage=cpu_usage,
            cpu_temp=cpu_temp,
            memory_total=memory_total,
            memory_used=memory_used,
            memory_percent=memory_percent,
            uptime=uptime if uptime else 0,
            version=vars_info.get("version", ""),
        )

    def _determine_status(
        self,
        array: Optional[UnraidArray],
        containers: list,
        vms: list,
        system: Optional[UnraidSystem] = None,
    ) -> StatusLevel:
        """Determine overall status based on array, containers, VMs, and system health.

        Temperature thresholds:
        - Disk: Warning > 50C, Critical > 60C
        - CPU: Warning > 80C, Critical > 95C
        """
        if not array:
            return StatusLevel.UNKNOWN

        # Track if we have warnings (but not errors)
        has_warning = False

        # Check array status (case-insensitive)
        if array.status.lower() != "started":
            return StatusLevel.ERROR

        # Check for disk faults and SMART failures
        for disk in array.disks:
            # Disk fault = ERROR
            if disk.status.lower() == "fault":
                return StatusLevel.ERROR

            # SMART failed = ERROR
            if disk.smart_status.lower() in ["failed", "fail"]:
                return StatusLevel.ERROR

            # SMART errors > 0 = WARNING
            if disk.num_errors > 0:
                has_warning = True

            # Disk temperature checks
            if disk.temp is not None:
                if disk.temp > 60:  # Critical temperature
                    return StatusLevel.ERROR
                elif disk.temp > 50:  # Warning temperature
                    has_warning = True

        # Check parity status
        parity_lower = array.parity_status.lower()
        if parity_lower in ["invalid", "degraded", "failed"]:
            return StatusLevel.ERROR
        if parity_lower in ["syncing", "checking", "rebuilding"]:
            has_warning = True

        # Check parity errors
        if array.parity_errors > 0:
            has_warning = True

        # Check CPU temperature if available
        if system and system.cpu_temp is not None:
            if system.cpu_temp > 95:  # Critical CPU temperature
                return StatusLevel.ERROR
            elif system.cpu_temp > 80:  # Warning CPU temperature
                has_warning = True

        # Return WARNING if any warning conditions were met
        if has_warning:
            return StatusLevel.WARNING

        return StatusLevel.HEALTHY


unraid_service = UnraidService()
