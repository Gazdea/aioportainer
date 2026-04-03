# EventListener

Listen to Docker events in real-time.

## Basic Usage

```python
import asyncio
from portainer import PortainerClient, EventListener

async def on_event(result):
    print(f"[endpoint {result.endpoint_id}] {result.event.type} {result.event.action}")

async def main():
    client = PortainerClient(url="https://portainer:9443", token="...")
    
    listener = EventListener(
        client,
        endpoint_id=None,  # None = all endpoints
        event_types=["container"],  # Filter by type
    )
    
    listener.register_callback(on_event)
    listener.start()
    
    await asyncio.sleep(60)  # Listen for 60 seconds
    
    listener.stop()

asyncio.run(main())
```

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| client | PortainerClient | - | Portainer client instance |
| endpoint_id | int \| None | None | Endpoint to listen (None = all) |
| event_types | list[str] \| None | None | Filter by types |
| reconnect_interval | float | 5 seconds | Reconnect delay |
| debug | bool | False | Enable debug logging |

### Event Types
- `container` - Container events (start, stop, die, etc.)
- `image` - Image events (pull, delete, etc.)
- `volume` - Volume events
- `network` - Network events
- `daemon` - Daemon events

## Callbacks

Callbacks receive `EventListenerResult`:

```python
def on_event(result):
    print(f"Endpoint: {result.endpoint_id}")
    print(f"Type: {result.event.type}")
    print(f"Action: {result.event.action}")
    print(f"Actor ID: {result.event.actor_id}")
    print(f"Attributes: {result.event.actor_attributes}")
    print(f"Time: {result.event.time}")
```

## Query Past Events

Use `get_recent_events()` to fetch historical events:

```python
from datetime import datetime, timedelta, timezone

listener = EventListener(client)

events = await listener.get_recent_events(
    endpoint_id=1,
    since=3600,  # Last hour
)

for event in events:
    print(f"{event.event.time}: {event.event.type} {event.event.action}")
```

## Properties

- `_running` - Check if listener is active

## Methods

- `start()` - Start the listener
- `stop()` - Stop the listener
- `register_callback(callback)` - Add callback
- `unregister_callback(callback)` - Remove callback
- `get_recent_events(endpoint_id, since)` - Get past events
