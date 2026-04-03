"""Tests for models."""
import pytest

from portainer.models import (
    Stack,
    Container,
    Endpoint,
    ContainerStats,
    User,
    Team,
    Registry,
    DockerEvent,
    EventListenerResult,
)


class TestModels:
    """Tests for data models."""

    def test_stack_properties(self):
        """Test Stack computed properties."""
        stack = Stack(id=1, name="test", endpoint_id=1, status=1)
        assert stack.is_active is True
        assert stack.is_error is False
        assert stack.status_text == "Active"

        stack_error = Stack(id=2, name="test2", endpoint_id=1, status=4)
        assert stack_error.is_active is False
        assert stack_error.is_error is True
        assert stack_error.status_text == "Error"

    def test_container_properties(self):
        """Test Container computed properties."""
        container = Container(
            id="abc123def456",
            name="test",
            image="nginx:latest",
            image_id="sha256:abc",
            state="running",
            status="Up 2 hours",
        )
        assert container.is_running is True
        assert container.short_id == "abc123def456"

        stopped = Container(
            id="def456",
            name="stopped",
            image="nginx:latest",
            image_id="sha256:def",
            state="exited",
            status="Exited 0",
        )
        assert stopped.is_running is False

    def test_container_stats(self):
        """Test ContainerStats computed properties."""
        stats = ContainerStats(
            container_id="test",
            memory_usage=104857600,  # 100 MB
            memory_limit=209715200,  # 200 MB
        )
        assert stats.memory_usage_mb == 100.0
        assert stats.memory_limit_mb == 200.0

    def test_user_is_admin(self):
        """Test User.is_admin property."""
        admin = User(id=1, username="admin", role=1)
        assert admin.is_admin is True

        user = User(id=2, username="user", role=2)
        assert user.is_admin is False

    def test_team_model(self):
        """Test Team model."""
        team = Team(id=1, name="developers")
        assert team.id == 1
        assert team.name == "developers"
        assert team.system is False

    def test_registry_model(self):
        """Test Registry model."""
        reg = Registry(id=1, name="dockerhub", type="dockerhub", url="docker.io")
        assert reg.id == 1
        assert reg.authentication is False

    def test_event_listener_result(self):
        """Test EventListenerResult model."""
        event = DockerEvent(
            type="container",
            action="start",
            actor_id="abc123",
            actor_attributes={"name": "test"},
            time=1234567890,
            time_nano=1234567890000000000,
        )
        result = EventListenerResult(endpoint_id=1, event=event)
        assert result.endpoint_id == 1
        assert result.event.type == "container"
        assert result.event.action == "start"
