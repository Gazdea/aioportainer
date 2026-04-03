# homelab-portainer

Async CLI for Portainer API with Git integration, health monitoring, image watching and event listening.

## Features

- **Async HTTP Client** - Full Portainer API coverage
- **Stack Management** - Git-based deploy with automatic commit/push/redeploy
- **Container Management** - Start, stop, restart, logs, stats
- **Health Monitoring** - Stack and container health checks
- **Image Watcher** - Monitor Docker images for updates
- **Event Listener** - Real-time Docker events streaming

## Installation

```bash
pip install -e .
```

## Quick Start

```python
import asyncio
from portainer import PortainerClient, StackManager

async def main():
    async with PortainerClient(
        url="https://portainer:9443",
        token="your-api-key",
    ) as client:
        sm = StackManager(client)
        stacks = await sm.list_stacks()
        for s in stacks:
            print(f"{s.name}: {s.status_text}")

asyncio.run(main())
```

## CLI Usage

```bash
# Set token
$env:PORTAINER_TOKEN="your-token"

# List stacks
portainer stack list --url "https://portainer:9443" --token $env:PORTAINER_TOKEN

# Deploy stack
portainer stack deploy mystack "update message"

# Monitor images
portainer watch images --interval 6

# Listen to events
portainer events start --duration 30
```

## Project Structure

```
portainer/
├── client.py         # HTTP client (Portainer API)
├── models.py         # Dataclass models
├── stack_manager.py  # Stack operations + git
├── container_manager.py  # Container operations
├── monitor.py        # Health monitoring
├── watcher.py        # ImageWatcher
├── listener.py       # EventListener
└── cli.py            # CLI
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Linting
ruff check portainer/

# Type checking
mypy portainer/
```

## License

MIT
