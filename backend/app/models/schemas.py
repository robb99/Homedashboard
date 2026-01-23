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
    data_usage_24h: float = 0.0
    wan_latency: float = 0.0


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


class PlexSession(BaseModel):
    user: str
    title: str  # Movie title or episode title
    show_title: Optional[str] = None  # For TV: show name
    type: str  # movie, episode
    progress: float = 0.0  # 0-100 percentage
    state: str = "playing"  # playing, paused


class PlexStatus(BaseStatus):
    recent_items: List[PlexItem] = []
    library_count: int = 0
    movie_count: int = 0
    show_count: int = 0
    active_sessions: List[PlexSession] = []


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
# WEATHER MODELS
# =============================================================================
class WeatherForecast(BaseModel):
    temperature: float
    description: str
    icon: str


class WeatherStatus(BaseStatus):
    today: Optional[WeatherForecast] = None
    tomorrow: Optional[WeatherForecast] = None
    location: Optional[str] = None


# =============================================================================
# NEWS MODELS
# =============================================================================
class NewsHeadline(BaseModel):
    title: str
    source: Optional[str] = None
    url: Optional[str] = None


class NewsStatus(BaseStatus):
    headlines: List[NewsHeadline] = []


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


# =============================================================================
# CONFIGURATION MODELS
# =============================================================================
class ServiceConfigStatus(BaseModel):
    """Status of a single service's configuration."""
    configured: bool = False
    has_credentials: bool = False


class ConfigStatus(BaseModel):
    """Overall configuration status for all services."""
    is_first_run: bool = True
    unifi: ServiceConfigStatus = ServiceConfigStatus()
    proxmox: ServiceConfigStatus = ServiceConfigStatus()
    plex: ServiceConfigStatus = ServiceConfigStatus()
    docker: ServiceConfigStatus = ServiceConfigStatus()
    calendar: ServiceConfigStatus = ServiceConfigStatus()
    weather: ServiceConfigStatus = ServiceConfigStatus()
    news: ServiceConfigStatus = ServiceConfigStatus()


class ConfigUpdate(BaseModel):
    """Configuration update payload - all fields optional for partial updates."""
    # UniFi
    unifi_host: Optional[str] = None
    unifi_username: Optional[str] = None
    unifi_password: Optional[str] = None
    unifi_site: Optional[str] = None
    unifi_verify_ssl: Optional[bool] = None
    unifi_enabled: Optional[bool] = None

    # Proxmox
    proxmox_host: Optional[str] = None
    proxmox_user: Optional[str] = None
    proxmox_token_name: Optional[str] = None
    proxmox_token_value: Optional[str] = None
    proxmox_node: Optional[str] = None
    proxmox_verify_ssl: Optional[bool] = None
    proxmox_enabled: Optional[bool] = None

    # Plex
    plex_url: Optional[str] = None
    plex_token: Optional[str] = None
    plex_enabled: Optional[bool] = None

    # Docker
    docker_host: Optional[str] = None
    docker_enabled: Optional[bool] = None

    # Google Calendar
    google_credentials_path: Optional[str] = None
    google_calendar_ids: Optional[str] = None
    calendar_enabled: Optional[bool] = None

    # Weather
    weather_latitude: Optional[float] = None
    weather_longitude: Optional[float] = None
    weather_enabled: Optional[bool] = None

    # News
    news_api_key: Optional[str] = None
    news_country: Optional[str] = None
    news_enabled: Optional[bool] = None

    # Application Settings
    poll_interval: Optional[int] = None
    cache_ttl: Optional[int] = None
    cors_origins: Optional[str] = None


class ConfigResponse(BaseModel):
    """Configuration response - passwords are masked."""
    # UniFi
    unifi_host: str = ""
    unifi_username: str = ""
    unifi_password: str = ""  # Will be masked
    unifi_site: str = "default"
    unifi_verify_ssl: bool = False
    unifi_enabled: bool = True

    # Proxmox
    proxmox_host: str = ""
    proxmox_user: str = ""
    proxmox_token_name: str = ""
    proxmox_token_value: str = ""  # Will be masked
    proxmox_node: str = "pve"
    proxmox_verify_ssl: bool = False
    proxmox_enabled: bool = True

    # Plex
    plex_url: str = ""
    plex_token: str = ""  # Will be masked
    plex_enabled: bool = True

    # Docker
    docker_host: str = ""
    docker_enabled: bool = True

    # Google Calendar
    google_credentials_path: str = ""
    google_calendar_ids: str = "primary"
    calendar_enabled: bool = True

    # Weather
    weather_latitude: float = 0.0
    weather_longitude: float = 0.0
    weather_enabled: bool = True

    # News
    news_api_key: str = ""  # Will be masked
    news_country: str = "us"
    news_enabled: bool = True

    # Application Settings
    poll_interval: int = 30
    cache_ttl: int = 25
    cors_origins: str = "http://localhost:3000"


class TestConnectionRequest(BaseModel):
    """Request payload for testing a service connection."""
    # Common fields - service determined by endpoint
    # UniFi
    unifi_host: Optional[str] = None
    unifi_username: Optional[str] = None
    unifi_password: Optional[str] = None
    unifi_site: Optional[str] = None
    unifi_verify_ssl: Optional[bool] = None

    # Proxmox
    proxmox_host: Optional[str] = None
    proxmox_user: Optional[str] = None
    proxmox_token_name: Optional[str] = None
    proxmox_token_value: Optional[str] = None
    proxmox_node: Optional[str] = None
    proxmox_verify_ssl: Optional[bool] = None

    # Plex
    plex_url: Optional[str] = None
    plex_token: Optional[str] = None

    # Docker
    docker_host: Optional[str] = None

    # Calendar
    google_credentials_path: Optional[str] = None

    # Weather
    weather_latitude: Optional[float] = None
    weather_longitude: Optional[float] = None

    # News
    news_api_key: Optional[str] = None


class TestConnectionResult(BaseModel):
    """Result of a connection test."""
    success: bool
    message: str
    details: Optional[str] = None


# =============================================================================
# LOGGING MODELS
# =============================================================================
class LogEntry(BaseModel):
    id: str
    timestamp: str
    level: str
    logger: str
    message: str
    details: Optional[str] = None


class LogsResponse(BaseModel):
    entries: List[LogEntry]
