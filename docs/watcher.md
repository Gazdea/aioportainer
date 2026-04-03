# ImageWatcher

Monitor Docker containers for available image updates.

## Basic Usage

```python
import asyncio
import datetime
from portainer import PortainerClient, ImageWatcher

async def main():
    client = PortainerClient(url="https://portainer:9443", token="...")
    
    watcher = ImageWatcher(
        client,
        interval=datetime.timedelta(hours=6),
        endpoint_id=None,  # None = all endpoints
    )
    
    watcher.start()
    
    await asyncio.sleep(30)  # Let first check complete
    
    for (ep_id, container_id), result in watcher.results.items():
        if result.status and result.status.update_available:
            print(f"Update for {result.container_name}: {result.image}")
    
    watcher.stop()

asyncio.run(main())
```

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| client | PortainerClient | - | Portainer client instance |
| interval | timedelta | 12 hours | Polling interval |
| endpoint_id | int \| None | None | Endpoint to monitor (None = all) |
| debug | bool | False | Enable debug logging |

## Results

`watcher.results` is a dictionary keyed by `(endpoint_id, container_id)` tuples:

```python
for (ep_id, container_id), result in watcher.results.items():
    print(result.endpoint_id)
    print(result.container_id)
    print(result.container_name)
    print(result.image)
    print(result.status.update_available)  # bool
    print(result.status.local_digest)
    print(result.status.registry_digest)
```

## Callbacks

Register callbacks to be notified after each poll:

```python
from portainer.models import ImageWatcherResult

async def on_result(result: ImageWatcherResult):
    if result.status and result.status.update_available:
        print(f"Update available for {result.container_name}")

watcher.register_callback(on_result)

# Later, to remove:
watcher.unregister_callback(on_result)
```

## Properties

- `results` - Current results dictionary
- `last_check` - Unix timestamp of last completed poll

## Methods

- `start()` - Start the watcher
- `stop()` - Stop the watcher
- `register_callback(callback)` - Add callback
- `unregister_callback(callback)` - Remove callback
