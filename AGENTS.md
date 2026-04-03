# AGENTS.md - Developer Guidelines

This file provides guidelines for agentic coding agents working in this repository.

## Project Overview

- **Name**: homelab-portainer
- **Type**: Async CLI for Portainer API
- **Python**: 3.9+
- **Dependencies**: aiohttp>=3.9.0, click>=8.0.0, urllib3>=2.0.0
- **Dev Dependencies**: pytest, pytest-asyncio, pytest-cov, syrupy, ruff, mypy, pre-commit
- **Docs**: mkdocs, mkdocs-material

## Build/Lint/Test Commands

### Installation
```bash
pip install -e ".[dev]"
pip install -e ".[docs]"
```

### Pre-commit
```bash
pre-commit install
pre-commit run --all-files
```

### Running the CLI
```bash
$env:PORTAINER_TOKEN="your-token"

# Stack commands
portainer stack list
portainer stack deploy mystack "commit message"

# Container commands
portainer container list 1 --stack mystack
portainer container stats 1 <container_id>
portainer container logs 1 <container_id>

# Image watcher
portainer watch images --interval 6

# Event listener
portainer events start --duration 30
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=portainer --cov-report=html

# Run single test
pytest tests/test_client.py::TestPortainerClient::test_get_stacks
pytest -k "test_name_pattern"

# Update snapshots
pytest --snapshot-update
```

### Linting & Type Checking
```bash
# Ruff check
ruff check portainer/
ruff check --fix portainer/

# MyPy type check
mypy portainer/
```

### Documentation
```bash
# Serve docs locally
mkdocs serve

# Build docs
mkdocs build
```

---

## Code Style Guidelines

### Imports
**Pattern**: stdlib → third-party → local (relative with `.` prefix)
```python
import asyncio
import os
from typing import Optional

import aiohttp
import click

from .client import PortainerClient
from .models import Stack, Container
```

### Formatting
- **Line length**: 100 characters max
- **Indentation**: 4 spaces
- **Blank lines**: Two between top-level definitions, one between methods

### Types
- Use type hints for all function signatures
- Use `list[T]`, `dict[K, V]`, `Optional[T]` from `typing`
- Use `@dataclass` for models with properties for computed values

### Naming
- **Classes**: `PascalCase` (e.g., `PortainerClient`)
- **Functions/methods**: `snake_case` (e.g., `get_stacks`)
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_private_method` prefix

### Async/Await
- All I/O operations must be async
- Use `async def` and `asyncio.run()` in CLI
- Always manage session lifecycle (connect/disconnect)

### CLI (Click)
- Use `@click.group()`, `@click.option()`, `@click.argument()`
- Pass context with `@click.pass_context`
- Always use async runner pattern

### Error Handling
- Use `try/except` for operations that may fail
- Use `raise_for_status()` on HTTP responses
- Return structured JSON error responses: `{"success": false, "data": null, "error": {...}}`

---

## File Organization

```
portainer/
├── client.py         # Low-level HTTP client (Portainer API)
├── models.py         # Dataclass models
├── stack_manager.py  # Stack operations + git deploy
├── container_manager.py  # Container operations
├── monitor.py        # Health monitoring
├── watcher.py        # ImageWatcher (image update monitoring)
├── listener.py       # EventListener (real-time events)
└── cli.py            # CLI entry points
```

---

## New Features (from pyportainer)

### ImageWatcher (`portainer/watcher.py`)
- Poll Portainer for container image updates
- Compare local digest vs registry digest
- Configurable interval (default 12h)
- Callbacks for notifications
- Usage:
```python
from portainer import PortainerClient, ImageWatcher

watcher = ImageWatcher(client, interval=timedelta(hours=6))
watcher.register_callback(on_result)
watcher.start()
```

### EventListener (`portainer/listener.py`)
- Stream Docker events in real-time
- Filter by event_types
- Auto-reconnect on errors
- `get_recent_events()` for historical queries
- Usage:
```python
from portainer import PortainerClient, EventListener

listener = EventListener(client, event_types=["container"])
listener.register_callback(on_event)
listener.start()
```

---

## Testing

### Test Structure
```
tests/
├── conftest.py      # Fixtures
├── test_client.py   # Client API tests
└── test_models.py   # Model tests
```

### Snapshot Testing (syrupy)
```python
def test_something(snapshot):
    result = do_something()
    assert result == snapshot
```

---

## Known Issues

1. Some API endpoints may need adjustment for specific Portainer versions
2. ImageWatcher digest comparison depends on registry availability

---

## Adding New Features

1. Add methods to appropriate class (client, manager, watcher, listener)
2. Add dataclass models to `models.py`
3. Add CLI commands to `cli.py`
4. Add tests to `tests/`
5. Add documentation to `docs/`
6. Run: `ruff check` and `pytest` before committing
