"""Event listener for real-time Docker events."""
import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Callable, Optional

from .client import PortainerClient

logger = logging.getLogger(__name__)


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


class EventListener:
    """Listen to Docker events in real-time."""

    def __init__(
        self,
        client: PortainerClient,
        endpoint_id: Optional[int] = None,
        event_types: Optional[list[str]] = None,
        reconnect_interval: float = 5.0,
        debug: bool = False,
    ):
        """Initialize event listener.

        Args:
            client: PortainerClient instance
            endpoint_id: Specific endpoint to listen to, None for all
            event_types: Filter by event types (container, image, volume, network, etc.)
            reconnect_interval: Seconds between reconnect attempts
            debug: Enable debug logging
        """
        self.client = client
        self.endpoint_id = endpoint_id
        self.event_types = event_types
        self.reconnect_interval = reconnect_interval
        self._running = False
        self._tasks: list[asyncio.Task] = []
        self._callbacks: list[Callable] = []

        if debug:
            logging.basicConfig(level=logging.DEBUG)

    def register_callback(self, callback: Callable) -> None:
        """Register callback for events."""
        self._callbacks.append(callback)

    def unregister_callback(self, callback: Callable) -> None:
        """Unregister callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    async def _listen_endpoint(self, endpoint_id: int) -> None:
        """Listen to events for a single endpoint."""
        logger.debug(f"Starting event listener for endpoint {endpoint_id}")

        while self._running:
            try:
                async for line in self.client.get_events_stream(endpoint_id):
                    if not self._running:
                        break

                    try:
                        event_data = json.loads(line)
                        event = self._parse_event(event_data)

                        if self.event_types and event.type not in self.event_types:
                            continue

                        result = EventListenerResult(endpoint_id=endpoint_id, event=event)

                        for callback in self._callbacks:
                            try:
                                if asyncio.iscoroutinefunction(callback):
                                    await callback(result)
                                else:
                                    callback(result)
                            except Exception as e:
                                logger.error(f"Callback error: {e}")

                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        logger.error(f"Event processing error: {e}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Event stream error for endpoint {endpoint_id}: {e}")
                await asyncio.sleep(self.reconnect_interval)

        logger.debug(f"Event listener stopped for endpoint {endpoint_id}")

    def _parse_event(self, data: dict) -> DockerEvent:
        """Parse event data."""
        actor = data.get("Actor", {})
        return DockerEvent(
            type=data.get("Type", ""),
            action=data.get("Action", ""),
            actor_id=actor.get("ID", ""),
            actor_attributes=actor.get("Attributes", {}),
            time=data.get("time", 0),
            time_nano=data.get("timeNano", 0),
        )

    async def get_recent_events(
        self,
        endpoint_id: int,
        since: int = 3600,
    ) -> list[EventListenerResult]:
        """Get recent events without streaming.

        Args:
            endpoint_id: Endpoint ID
            since: Seconds in the past

        Returns:
            List of EventListenerResult
        """
        raw_events = await self.client.get_recent_events(endpoint_id, since)
        results = []

        for event_data in raw_events:
            event = self._parse_event(event_data)
            if self.event_types and event.type not in self.event_types:
                continue
            results.append(EventListenerResult(endpoint_id=endpoint_id, event=event))

        return results

    async def _run(self) -> None:
        """Run the listener for all endpoints."""
        endpoints = await self.client.get_endpoints()

        for ep in endpoints:
            ep_id = ep.get("Id")
            if self.endpoint_id and ep_id != self.endpoint_id:
                continue

            task = asyncio.create_task(self._listen_endpoint(ep_id))
            self._tasks.append(task)

        await asyncio.gather(*self._tasks, return_exceptions=True)

    def start(self) -> None:
        """Start the listener."""
        if self._running:
            return
        self._running = True
        self._tasks = [asyncio.create_task(self._run())]
        logger.info(f"EventListener started (endpoint_id={self.endpoint_id}, types={self.event_types})")

    def stop(self) -> None:
        """Stop the listener."""
        self._running = False
        for task in self._tasks:
            task.cancel()
        self._tasks = []
        logger.info("EventListener stopped")
