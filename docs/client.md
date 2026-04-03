# PortainerClient API

## Initialization

```python
from portainer import PortainerClient

client = PortainerClient(
    url="https://portainer:9443",
    token="your-api-key",
    endpoints=["1", "2"],  # Optional: list of endpoint IDs
    timeout=30,
)
```

## Context Manager

```python
async with client:
    # client is connected
    pass
```

Or manually:

```python
await client.connect()
# ... use client
await client.disconnect()
```

## Endpoints

### get_endpoints() -> list[dict]
Get all Docker endpoints.

```python
endpoints = await client.get_endpoints()
```

### get_endpoint(endpoint_id: str) -> dict
Get endpoint details.

```python
ep = await client.get_endpoint("1")
```

## Stacks

### get_stacks(endpoint_id: str = None) -> list[dict]
Get stacks from endpoint(s).

### get_stack(name: str, endpoint_id: str = None) -> dict
Get stack by name.

### get_stack_details(stack_id: int, endpoint_id: int) -> dict
Get full stack details.

### redeploy_stack(stack_id: int, endpoint_id: int, auth: bool = True) -> dict
Trigger stack redeploy from Git.

## Containers

### get_containers(endpoint_id: str, all: bool = True) -> list[dict]
Get containers from endpoint.

### get_container_logs(endpoint_id: str, container_id: str, tail: int = 50) -> str
Get container logs.

### get_container_stats(endpoint_id: str, container_id: str) -> dict
Get container resource stats.

### start_container(endpoint_id: str, container_id: str)
### stop_container(endpoint_id: str, container_id: str)
### restart_container(endpoint_id: str, container_id: str)

## Users

### get_users() -> list[dict]
### get_user(user_id: int) -> dict
### create_user(username: str, password: str, role: int = 1) -> dict
### update_user(user_id: int, data: dict) -> dict
### delete_user(user_id: int) -> dict
### get_user_memberships(user_id: int) -> list[dict]

## Teams

### get_teams() -> list[dict]
### get_team(team_id: int) -> dict
### create_team(name: str) -> dict
### delete_team(team_id: int) -> dict
### get_team_members(team_id: int) -> list[dict]
### add_team_member(team_id: int, user_id: int) -> dict
### remove_team_member(team_id: int, user_id: int) -> dict

## Registries

### get_registries() -> list[dict]
### get_registry(registry_id: int) -> dict
### create_registry(name: str, registry_type: str, url: str = "", username: str = "", password: str = "") -> dict
### update_registry(registry_id: int, data: dict) -> dict
### delete_registry(registry_id: int) -> dict

## Images

### list_images(endpoint_id: str) -> list[dict]
### pull_image(endpoint_id: str, image: str, registry: str = "", tag: str = "latest") -> dict
### delete_image(endpoint_id: str, image_id: str, force: bool = False) -> dict
### get_image_digest(endpoint_id: str, image: str) -> dict

## Volumes

### get_volumes(endpoint_id: str) -> list[dict]
### create_volume(endpoint_id: str, name: str, driver: str = "local") -> dict
### delete_volume(endpoint_id: str, name: str) -> dict

## Networks

### get_networks(endpoint_id: str) -> list[dict]
### create_network(endpoint_id: str, name: str, driver: str = "bridge", subnet: str = "") -> dict
### delete_network(endpoint_id: str, network_id: str) -> dict

## Settings

### get_settings() -> dict
### update_settings(data: dict) -> dict

## Docker Hub

### search_dockerhub(term: str, limit: int = 25) -> list[dict]
Search Docker Hub for images.

## Edge Jobs

### get_edge_jobs() -> list[dict]
### get_edge_job(job_id: int) -> dict
### create_edge_job(name: str, cron: str = "", paths: list[str] = None) -> dict
### delete_edge_job(job_id: int) -> dict
### execute_edge_job(job_id: int, endpoint_ids: list[int]) -> dict

## Events

### get_recent_events(endpoint_id: int, since: int = 3600) -> list[dict]
Get recent Docker events.

### get_events_stream(endpoint_id: int)
Stream Docker events (async generator).
