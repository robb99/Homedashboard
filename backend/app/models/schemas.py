from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


class StatusLevel(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"


class BaseStatus(BaseModel):
    status: StatusLevel = StatusLevel.UNKNOWN
    last_updated: datetime = datetime.now()
    error_message: Optional[str] = None


# =============================================================================
# UNIFI MODELS
# =============================================================================
class UnifiDevice(BaseModel):
    name: str
    mac: str
    model: str
    ip: Optional[str] = None
    status: str
    uptime: Optional[int] = None
    type: str  # uap, usw, ugw, etc.


class UnifiClient(BaseModel):
    hostname: Optional[str] = None
    mac: str
    ip: Optional[str] = None
    network: Optional[str] = None
    is_wired: bool = False


class UnifiStatus(BaseStatus):
    devices: List[UnifiDevice] = []
    clients: List[UnifiClient] = []
    device_count: int = 0
    client_count: int = 0
    devices_online: int = 0
    devices_offline: int = 0
    wireless_clients: int = 0
    data_usage_24h: int = 0


# =============================================================================
# PROXMOX MODELS
# =============================================================================
class ProxmoxContainer(BaseModel):
    vmid: int
    name: str
    status: str  # running, stopped
    type: str  # lxc, qemu
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    memory_total: int = 0
    disk_usage: float = 0.0
    uptime: Optional[int] = None


class ProxmoxNode(BaseModel):
    name: str
    status: str
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    memory_total: int = 0
    uptime: Optional[int] = None


class ProxmoxStatus(BaseStatus):
    node: Optional[ProxmoxNode] = None
    containers: List[ProxmoxContainer] = []
    vms: List[ProxmoxContainer] = []
    total_running: int = 0
    total_stopped: int = 0


# =============================================================================
# PLEX MODELS
# =============================================================================
class PlexItem(BaseModel):
    title: str
    type: str  # movie, episode, track
    added_at: datetime
    thumb: Optional[str] = None
    year: Optional[int] = None
    grandparent_title: Optional[str] = None  # For episodes (show name)
    parent_title: Optional[str] = None  # For episodes (season name)


class PlexStatus(BaseStatus):
    recent_items: List[PlexItem] = []
    library_count: int = 0


# =============================================================================
# DOCKER MODELS
# =============================================================================
class DockerContainer(BaseModel):
    id: str
    name: str
    image: str
    status: str
    state: str  # running, exited, paused
    created: datetime
    ports: List[str] = []


class DockerStatus(BaseStatus):
    containers: List[DockerContainer] = []
    running_count: int = 0
    stopped_count: int = 0
    total_count: int = 0


# =============================================================================
# CALENDAR MODELS
# =============================================================================
class CalendarEvent(BaseModel):
    id: str
    summary: str
    start: datetime
    end: datetime
    all_day: bool = False
    location: Optional[str] = None
    calendar_name: Optional[str] = None


class CalendarStatus(BaseStatus):
    events: List[CalendarEvent] = []
    event_count: int = 0


# =============================================================================
# DASHBOARD AGGREGATE
# =============================================================================
class DashboardStatus(BaseModel):
    unifi: UnifiStatus
    proxmox: ProxmoxStatus
    plex: PlexStatus
    docker: DockerStatus
    calendar: CalendarStatus
    last_updated: datetime = datetime.now()
