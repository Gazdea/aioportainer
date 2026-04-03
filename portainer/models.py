"""Portainer API models."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ImageUpdateStatus:
    """Image update status."""

    update_available: bool = False
    local_digest: Optional[str] = None
    registry_digest: Optional[str] = None


@dataclass
class ImageWatcherResult:
    """Image watcher result."""

    endpoint_id: int
    container_id: str
    container_name: str
    image: str
    status: Optional[ImageUpdateStatus] = None


@dataclass
class DockerEvent:
    """Docker event data."""

    type: str
    action: str
    actor_id: str
    actor_attributes: dict
    time: int
    time_nano: int


@dataclass
class EventListenerResult:
    """Event listener result."""

    endpoint_id: int
    event: DockerEvent


@dataclass
class User:
    """User model."""

    id: int
    username: str
    role: int  # 1=admin, 2=user
    email: str = ""
    theme: str = ""
    last_seen: int = 0

    @property
    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self.role == 1


@dataclass
class Team:
    """Team model."""

    id: int
    name: str
    system: bool = False


@dataclass
class Registry:
    """Registry model."""

    id: int
    name: str
    type: str
    url: str = ""
    authentication: bool = False
    username: str = ""


@dataclass
class Volume:
    """Volume model."""

    name: str
    driver: str = "local"
    mountpoint: str = ""
    created_at: str = ""


@dataclass
class Network:
    """Network model."""

    id: str
    name: str
    driver: str = "bridge"
    scope: str = "local"
    subnet: str = ""


@dataclass
class EdgeJob:
    """Edge job model."""

    id: int
    name: str
    cron: str = ""
    paths: list[str] = field(default_factory=list)
    created_at: int = 0


@dataclass
class Endpoint:
    """Docker endpoint model."""
    id: int
    name: str
    url: str
    status: str
    status_message: str
    public_url: str = ""
    group_id: int = 0
    type: int = 1


@dataclass
class Stack:
    """Stack model."""
    id: int
    name: str
    endpoint_id: int
    status: int  # 1=Active, 2=Inactive, 3=Removing, 4=Error
    state: str = ""
    project_path: str = ""
    git_url: str = ""
    git_reference: str = ""
    git_config_path: str = ""
    created_by: str = ""
    creation_date: int = 0
    update_date: int = 0

    @property
    def status_text(self) -> str:
        """Human-readable status."""
        return {1: "Active", 2: "Inactive", 3: "Removing", 4: "Error"}.get(self.status, "Unknown")

    @property
    def is_error(self) -> bool:
        """Check if stack has error."""
        return self.status == 4

    @property
    def is_active(self) -> bool:
        """Check if stack is active."""
        return self.status == 1


@dataclass
class Container:
    """Docker container model."""
    id: str
    name: str
    image: str
    image_id: str
    state: str  # running, exited, paused, created
    status: str  # Up 2 hours, Exited (0) 3 days ago
    labels: dict = field(default_factory=dict)
    ports: dict = field(default_factory=dict)
    endpoint_id: int = 0

    @property
    def is_running(self) -> bool:
        """Check if container is running."""
        return self.state == "running"

    @property
    def short_id(self) -> str:
        """Get short container ID."""
        return self.id[:12]


@dataclass
class ContainerStats:
    """Container resource statistics."""
    container_id: str
    cpu_percent: float = 0.0
    memory_usage: int = 0
    memory_limit: int = 0
    memory_percent: float = 0.0
    network_rx: int = 0
    network_tx: int = 0
    block_read: int = 0
    block_write: int = 0

    @property
    def memory_usage_mb(self) -> float:
        """Memory usage in MB."""
        return self.memory_usage / 1024 / 1024

    @property
    def memory_limit_mb(self) -> float:
        """Memory limit in MB."""
        return self.memory_limit / 1024 / 1024


@dataclass
class StackDeployment:
    """Stack deployment result."""
    stack: Stack
    success: bool
    message: str
    containers: list["Container"] = field(default_factory=list)
    logs: str = ""
