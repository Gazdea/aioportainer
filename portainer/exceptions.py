"""Custom exceptions for Portainer API."""
from typing import Any, Optional


class PortainerError(Exception):
    """Base exception for Portainer API."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class PortainerConnectionError(PortainerError):
    """Connection to Portainer failed."""
    pass


class AuthenticationError(PortainerError):
    """Authentication failed."""
    pass


class NotFoundError(PortainerError):
    """Resource not found."""
    pass


class ValidationError(PortainerError):
    """Invalid input or validation failed."""
    pass


class PortainerTimeoutError(PortainerError):
    """Operation timed out."""
    pass


class RateLimitError(PortainerError):
    """Rate limit exceeded."""
    pass
