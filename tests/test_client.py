"""Tests for PortainerClient."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from portainer.client import PortainerClient


class TestPortainerClient:
    """Tests for PortainerClient."""

    @pytest.mark.asyncio
    async def test_get_endpoints(self, client, mock_session):
        """Test getting endpoints."""
        mock_resp = AsyncMock()
        mock_resp.json = AsyncMock(return_value=[{"Id": 1, "Name": "local"}])
        mock_resp.raise_for_status = MagicMock()

        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await client.get_endpoints()

        assert len(result) == 1
        assert result[0]["Id"] == 1

    @pytest.mark.asyncio
    async def test_get_stacks(self, client, mock_session):
        """Test getting stacks."""
        mock_resp = AsyncMock()
        mock_resp.json = AsyncMock(return_value=[{"Id": 1, "Name": "stack1", "Status": 1}])
        mock_resp.raise_for_status = MagicMock()

        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await client.get_stacks("1")

        assert len(result) == 1
        assert result[0]["Name"] == "stack1"

    @pytest.mark.asyncio
    async def test_get_containers(self, client, mock_session):
        """Test getting containers."""
        mock_resp = AsyncMock()
        mock_resp.json = AsyncMock(return_value=[{"Id": "abc", "Names": ["/test"]}])
        mock_resp.raise_for_status = MagicMock()

        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await client.get_containers("1")

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_status(self, client, mock_session):
        """Test getting status."""
        mock_resp = AsyncMock()
        mock_resp.json = AsyncMock(return_value={"Version": "2.19.0"})
        mock_resp.raise_for_status = MagicMock()

        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await client.get_status()

        assert result["Version"] == "2.19.0"

    @pytest.mark.asyncio
    async def test_get_users(self, client, mock_session):
        """Test getting users."""
        mock_resp = AsyncMock()
        mock_resp.json = AsyncMock(return_value=[{"Id": 1, "Username": "admin", "Role": 1}])
        mock_resp.raise_for_status = MagicMock()

        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await client.get_users()

        assert len(result) == 1
        assert result[0]["Username"] == "admin"

    @pytest.mark.asyncio
    async def test_get_teams(self, client, mock_session):
        """Test getting teams."""
        mock_resp = AsyncMock()
        mock_resp.json = AsyncMock(return_value=[{"Id": 1, "Name": "admins"}])
        mock_resp.raise_for_status = MagicMock()

        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await client.get_teams()

        assert len(result) == 1
        assert result[0]["Name"] == "admins"

    @pytest.mark.asyncio
    async def test_get_registries(self, client, mock_session):
        """Test getting registries."""
        mock_resp = AsyncMock()
        mock_resp.json = AsyncMock(return_value=[{"Id": 1, "Name": "dockerhub", "Type": "dockerhub"}])
        mock_resp.raise_for_status = MagicMock()

        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await client.get_registries()

        assert len(result) == 1
        assert result[0]["Name"] == "dockerhub"