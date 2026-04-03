# Models

## Core Models

### Stack
```python
@dataclass
class Stack:
    id: int
    name: str
    endpoint_id: int
    status: int  # 1=Active, 2=Inactive, 3=Removing, 4=Error
    state: str
    project_path: str
    git_url: str
    git_reference: str
    git_config_path: str
    created_by: str
    creation_date: int
    update_date: int
```

Properties:
- `status_text` - Human-readable status
- `is_error` - Check if stack has error
- `is_active` - Check if stack is active

### Container
```python
@dataclass
class Container:
    id: str
    name: str
    image: str
    image_id: str
    state: str  # running, exited, paused, created
    status: str  # Up 2 hours, Exited (0) 3 days ago
    labels: dict
    ports: dict
    endpoint_id: int
```

Properties:
- `is_running` - Check if container is running
- `short_id` - Get short container ID (first 12 chars)

### ContainerStats
```python
@dataclass
class ContainerStats:
    container_id: str
    cpu_percent: float
    memory_usage: int
    memory_limit: int
    memory_percent: float
    network_rx: int
    network_tx: int
    block_read: int
    block_write: int
```

Properties:
- `memory_usage_mb` - Memory usage in MB
- `memory_limit_mb` - Memory limit in MB

### Endpoint
```python
@dataclass
class Endpoint:
    id: int
    name: str
    url: str
    status: str
    status_message: str
    public_url: str
    group_id: int
    type: int
```

### User
```python
@dataclass
class User:
    id: int
    username: str
    role: int  # 1=admin, 2=user
    email: str
    theme: str
    last_seen: int
```

Properties:
- `is_admin` - Check if user is admin

### Team
```python
@dataclass
class Team:
    id: int
    name: str
    system: bool
```

### Registry
```python
@dataclass
class Registry:
    id: int
    name: str
    type: str
    url: str
    authentication: bool
    username: str
```

## Watcher/Listener Models

### ImageUpdateStatus
```python
@dataclass
class ImageUpdateStatus:
    update_available: bool
    local_digest: Optional[str]
    registry_digest: Optional[str]
```

### ImageWatcherResult
```python
@dataclass
class ImageWatcherResult:
    endpoint_id: int
    container_id: str
    container_name: str
    image: str
    status: Optional[ImageUpdateStatus]
```

### DockerEvent
```python
@dataclass
class DockerEvent:
    type: str
    action: str
    actor_id: str
    actor_attributes: dict
    time: int
    time_nano: int
```

### EventListenerResult
```python
@dataclass
class EventListenerResult:
    endpoint_id: int
    event: DockerEvent
```
