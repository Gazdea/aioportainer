"""Test fixtures for portainer tests."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from portainer.client import PortainerClient
from portainer.models import Stack, Container, Endpoint


@pytest.fixture
def mock_session():
    """Create mock aiohttp session."""
    session = MagicMock()
    session.get = AsyncMock()
    session.post = AsyncMock()
    session.put = AsyncMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
async def client(mock_session):
    """Create PortainerClient with mock session."""
    client = PortainerClient(
        url="https://test:9443",
        token="test-token",
        endpoints=["1"],
    )
    client._session = mock_session
    return client


@pytest.fixture
def sample_stack():
    """Create sample Stack."""
    return Stack(
        id=1,
        name="test-stack",
        endpoint_id=1,
        status=1,
        state="active",
        git_url="https://github.com/test/repo",
    )


@pytest.fixture
def sample_container():
    """Create sample Container."""
    return Container(
        id="abc123def456",
        name="test-container",
        image="nginx:latest",
        image_id="sha256:abc123",
        state="running",
        status="Up 2 hours",
    )


@pytest.fixture
def sample_endpoint():
    """Create sample Endpoint."""
    return Endpoint(
        id=1,
        name="local",
        url="unix:///var/run/docker.sock",
        status="UP",
        status_message="Ready",
    )
