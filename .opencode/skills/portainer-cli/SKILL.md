---
name: portainer-cli
description: Async CLI for Portainer API - stack management, container control, health monitoring, image watcher, and event listener
license: MIT
compatibility: opencode
metadata:
  audience: maintainers
  workflow: portainer
---

## Overview

This is an async Python CLI for managing Portainer - a GUI for Docker. Provides stack deployment, container management, health monitoring, image update watching, and Docker event streaming.

## Project Structure

```
portainer/
├── client.py         # Low-level HTTP client (Portainer API)
├── models.py         # Dataclass models (14 models)
├── stack_manager.py  # Stack operations + git deploy
├── container_manager.py  # Container operations
├── monitor.py        # Health monitoring
├── watcher.py        # ImageWatcher (image update monitoring)
├── listener.py       # EventListener (real-time events)
└── cli.py            # CLI entry points

tests/
├── conftest.py      # Fixtures
├── test_client.py   # Client API tests
└── test_models.py   # Model tests
```

## Requirements

- **Python**: 3.9+
- **Dependencies**: aiohttp>=3.9.0, click>=8.0.0, urllib3>=2.0.0
- **Dev**: pytest, pytest-asyncio, pytest-cov, syrupy, ruff, mypy, pre-commit
- **Docs**: mkdocs, mkdocs-material

## Installation

```bash
pip install -e ".[dev]"
pip install -e ".[docs]"
```

## API Methods (client.py)

### Endpoints
- `get_endpoints()` - Get all endpoints
- `get_endpoint(endpoint_id)` - Get endpoint details

### Stacks
- `get_stacks(endpoint_id?)` - Get stacks from endpoint(s)
- `get_stack(name, endpoint_id?)` - Get stack by name
- `get_stack_details(stack_id, endpoint_id)` - Get stack details
- `redeploy_stack(stack_id, endpoint_id, auth?)` - Trigger Git redeploy

### Containers
- `get_containers(endpoint_id, show_all?)` - Get containers
- `get_container_logs(endpoint_id, container_id, tail?)` - Get logs
- `get_container_stats(endpoint_id, container_id)` - Get stats
- `start_container(endpoint_id, container_id)` - Start container
- `stop_container(endpoint_id, container_id)` - Stop container
- `restart_container(endpoint_id, container_id)` - Restart container

### Users & Teams
- `get_users()` - Get all users
- `get_user(user_id)` - Get user by ID
- `create_user(username, password, role?)` - Create user (role: 1=admin, 2=user)
- `update_user(user_id, data)` - Update user
- `delete_user(user_id)` - Delete user
- `get_user_memberships(user_id)` - Get user team memberships
- `get_teams()` - Get all teams
- `get_team(team_id)` - Get team by ID
- `create_team(name)` - Create team
- `delete_team(team_id)` - Delete team
- `get_team_members(team_id)` - Get team members
- `add_team_member(team_id, user_id)` - Add user to team
- `remove_team_member(team_id, user_id)` - Remove user from team

### Registries
- `get_registries()` - Get all registries
- `get_registry(registry_id)` - Get registry by ID
- `create_registry(name, type, url?, username?, password?)` - Create registry
- `update_registry(registry_id, data)` - Update registry
- `delete_registry(registry_id)` - Delete registry

### Images
- `list_images(endpoint_id)` - List images
- `pull_image(endpoint_id, image, registry?, tag?)` - Pull image
- `delete_image(endpoint_id, image_id, force?)` - Delete image
- `get_image_digest(endpoint_id, image)` - Get image digest

### Volumes
- `get_volumes(endpoint_id)` - Get volumes
- `create_volume(endpoint_id, name, driver?)` - Create volume
- `delete_volume(endpoint_id, name)` - Delete volume

### Networks
- `get_networks(endpoint_id)` - Get networks
- `create_network(endpoint_id, name, driver?, subnet?)` - Create network
- `delete_network(endpoint_id, network_id)` - Delete network

### Settings & System
- `get_settings()` - Get Portainer settings
- `update_settings(data)` - Update settings
- `get_status()` - Get Portainer status
- `get_version()` - Get Portainer version
- `search_dockerhub(term, limit?)` - Search Docker Hub

### Edge Jobs
- `get_edge_jobs()` - Get all edge jobs
- `get_edge_job(job_id)` - Get edge job by ID
- `create_edge_job(name, cron?, paths?)` - Create edge job
- `delete_edge_job(job_id)` - Delete edge job
- `execute_edge_job(job_id, endpoint_ids)` - Execute edge job

### Events
- `get_recent_events(endpoint_id, since?)` - Get recent Docker events
- `get_events_stream(endpoint_id)` - Stream Docker events (generator)

## Models (models.py)

```python
from portainer import (
    PortainerClient,
    Stack,              # Stack with status properties
    Container,          # Container with is_running, short_id
    Endpoint,            # Docker endpoint
    ContainerStats,      # CPU, RAM, Network, Block stats
    StackDeployment,    # Deployment result
    User,               # User with is_admin property
    Team,
    Registry,
    Volume,
    Network,
    EdgeJob,
    ImageUpdateStatus,  # Image update detection
    ImageWatcherResult,
    DockerEvent,
    EventListenerResult,
)
```

## CLI Commands

### Environment

```bash
$env:PORTAINER_TOKEN="your-token"
```

### Stack Commands

```bash
# List all stacks
portainer stack list

# Deploy stack (git commit + push + redeploy)
portainer stack deploy mystack "commit message"

# Stack status
portainer stack status mystack

# Stack containers
portainer stack containers mystack
```

### Container Commands

```bash
# List containers on endpoint
portainer container list 1
portainer container list 1 --stack mystack

# Container logs
portainer container logs 1 <container_id> --lines 50

# Container stats
portainer container stats 1 <container_id>

# Container control
portainer container start 1 <container_id>
portainer container stop 1 <container_id>
portainer container restart 1 <container_id>
```

### Health Commands

```bash
# Check stack health
portainer health check mystack

# Check all stacks
portainer health all

# System stats
portainer system stats
```

### Image Watcher

```bash
# Monitor image updates
portainer watch images --interval 6
portainer watch images --interval 12 --endpoint 1
```

### Event Listener

```bash
# Listen to Docker events
portainer events start --duration 30
portainer events start --types container,image --duration 60

# Recent events
portainer events list 1 --since 3600
```

## Code Style

### Imports

```python
import asyncio
import os
from typing import Optional

import aiohttp
import click

from .client import PortainerClient
from .models import Stack, Container
```

### Rules

- Line length: 100 characters max
- Indentation: 4 spaces
- Use type hints for all functions
- Use `@dataclass` for models
- All I/O must be async
- Use Click with `@click.group()`, async runner pattern

### Error Handling

```python
try:
    # operation
except Exception:
    raise_for_status()  # on HTTP responses
```

Return structured JSON: `{"success": false, "data": null, "error": {...}}`

## Testing

```bash
# Run all tests
pytest

# Single test
pytest tests/test_client.py::TestPortainerClient::test_get_stacks

# With coverage
pytest --cov=portainer --cov-report=html

# Update snapshots
pytest --snapshot-update
```

## Linting

```bash
ruff check portainer/
ruff check --fix portainer/
mypy portainer/
```

## Adding Features

1. Add methods to appropriate class (client, manager, watcher, listener)
2. Add dataclass models to `models.py`
3. Add CLI commands to `cli.py`
4. Add tests to `tests/`
5. Add documentation to `docs/`
6. Run: `ruff check` and `pytest` before committing
