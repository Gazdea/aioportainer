# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-04-04

### Added
- **Async HTTP Client** - Full Portainer API coverage
- **Stack Management** - Git-based deploy with automatic commit/push/redeploy
- **Container Management** - Start, stop, restart, logs, stats
- **Health Monitoring** - Stack and container health checks
- **Image Watcher** - Monitor Docker images for updates
- **Event Listener** - Real-time Docker events streaming

### New API Endpoints
- Users: get, create, update, delete, memberships
- Teams: get, create, delete, members
- Registries: get, create, update, delete
- Images: list, pull, delete, digest
- Volumes: get, create, delete
- Networks: get, create, delete
- Settings: get, update
- Docker Hub: search
- Edge Jobs: get, create, delete, execute

### New Models
- User, Team, Registry, Volume, Network, EdgeJob
- ImageUpdateStatus, ImageWatcherResult
- DockerEvent, EventListenerResult

### CLI Commands
- `portainer watch images` - Monitor image updates
- `portainer events start` - Listen to Docker events
- `portainer events list` - Get recent events

### Improvements
- Connection pooling in PortainerClient
- Custom exceptions with proper error handling
- Retry decorator with exponential backoff

### Dependencies
- aiohttp>=3.9.0
- click>=8.0.0
- urllib3>=2.0.0