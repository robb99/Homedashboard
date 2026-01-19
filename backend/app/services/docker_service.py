import docker
from datetime import datetime
import logging

from app.config import get_settings
from app.models.schemas import DockerStatus, DockerContainer, StatusLevel
from app.services.cache import cache_service

logger = logging.getLogger(__name__)

CACHE_KEY = "docker_status"


class DockerService:
    def __init__(self):
        self.settings = get_settings()
        self._client = None

    def _get_client(self):
        """Get Docker client, connecting to remote or local socket."""
        if self._client is None:
            try:
                if self.settings.docker_host:
                    self._client = docker.DockerClient(
                        base_url=self.settings.docker_host
                    )
                else:
                    self._client = docker.from_env()
            except Exception as e:
                logger.error(f"Failed to connect to Docker: {e}")
                return None
        return self._client

    async def get_status(self, use_cache: bool = True) -> DockerStatus:
        """Get Docker container status."""
        if use_cache:
            cached = await cache_service.get(CACHE_KEY)
            if cached:
                return cached

        try:
            client = self._get_client()
            if client is None:
                return DockerStatus(
                    status=StatusLevel.UNKNOWN,
                    error_message="Docker not available",
                    last_updated=datetime.now(),
                )

            # Get all containers
            all_containers = client.containers.list(all=True)

            containers = []
            running_count = 0
            stopped_count = 0

            for c in all_containers:
                # Parse port mappings
                ports = []
                port_bindings = c.attrs.get("NetworkSettings", {}).get("Ports", {})
                if port_bindings:
                    for container_port, host_bindings in port_bindings.items():
                        if host_bindings:
                            for binding in host_bindings:
                                host_port = binding.get("HostPort", "")
                                ports.append(f"{host_port}:{container_port}")

                container = DockerContainer(
                    id=c.short_id,
                    name=c.name,
                    image=c.image.tags[0] if c.image.tags else c.image.short_id,
                    status=c.status,
                    state=c.attrs.get("State", {}).get("Status", "unknown"),
                    created=datetime.fromisoformat(
                        c.attrs.get("Created", "").replace("Z", "+00:00")
                    ),
                    ports=ports,
                )
                containers.append(container)

                if c.status == "running":
                    running_count += 1
                else:
                    stopped_count += 1

            # Sort by name
            containers.sort(key=lambda x: x.name.lower())

            # Determine status
            if stopped_count > 0 and running_count > 0:
                status = StatusLevel.WARNING
            elif running_count > 0:
                status = StatusLevel.HEALTHY
            elif len(containers) == 0:
                status = StatusLevel.UNKNOWN
            else:
                status = StatusLevel.WARNING

            result = DockerStatus(
                status=status,
                containers=containers,
                running_count=running_count,
                stopped_count=stopped_count,
                total_count=len(containers),
                last_updated=datetime.now(),
            )

            await cache_service.set(CACHE_KEY, result)
            return result

        except Exception as e:
            logger.error(f"Docker error: {e}")
            return DockerStatus(
                status=StatusLevel.ERROR,
                error_message=str(e),
                last_updated=datetime.now(),
            )


docker_service = DockerService()
