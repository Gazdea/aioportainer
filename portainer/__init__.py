#!/usr/bin/env python3
"""Portainer API module for Homelab."""
import sys

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from .cli import cli
from .client import PortainerClient
from .container_manager import ContainerManager
from .exceptions import (
    AuthenticationError,
    NotFoundError,
    PortainerConnectionError,
    PortainerError,
    PortainerTimeoutError,
    RateLimitError,
    ValidationError,
)
from .listener import EventListener
from .models import (
    Container,
    ContainerStats,
    DockerEvent,
    EdgeJob,
    Endpoint,
    EventListenerResult,
    ImageUpdateStatus,
    ImageWatcherResult,
    Network,
    Registry,
    Stack,
    StackDeployment,
    Team,
    User,
    Volume,
)
from .monitor import HealthMonitor
from .retry import retry, retry_sync
from .stack_manager import StackManager
from .watcher import ImageWatcher

__all__ = [
    # Client
    "PortainerClient",
    # Exceptions
    "PortainerError",
    "PortainerConnectionError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "PortainerTimeoutError",
    "RateLimitError",
    # Models
    "Stack",
    "Container",
    "Endpoint",
    "ContainerStats",
    "StackDeployment",
    "User",
    "Team",
    "Registry",
    "Volume",
    "Network",
    "EdgeJob",
    "ImageUpdateStatus",
    "ImageWatcherResult",
    "DockerEvent",
    "EventListenerResult",
    # Managers
    "StackManager",
    "ContainerManager",
    "HealthMonitor",
    "ImageWatcher",
    "EventListener",
    # Utils
    "retry",
    "retry_sync",
    # CLI
    "cli",
]
