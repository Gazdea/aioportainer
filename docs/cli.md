# CLI Reference

## Global Options

```bash
--url URL          Portainer URL (default: https://gaz-linux:9443)
--token TOKEN      Portainer API Token (required)
```

## Stack Commands

### stack list
List all stacks.
```bash
portainer stack list
```

### stack status
Get stack status by name.
```bash
portainer stack status <name>
```

### stack deploy
Deploy stack (commit + push + redeploy + monitor).
```bash
portainer stack deploy <name> [message]
portainer stack deploy mystack "Update config" --poll-interval 5 --max-retries 24
```

Options:
- `--poll-interval` - Polling interval in seconds (default: 5)
- `--max-retries` - Max polling attempts (default: 24)

### stack containers
List containers in a stack.
```bash
portainer stack containers <name>
```

## Container Commands

### container list
List containers on endpoint.
```bash
portainer container list <endpoint>
portainer container list 1 --stack mystack
```

Options:
- `--stack` - Filter by stack name

### container logs
Get container logs.
```bash
portainer container logs <endpoint> <container_id>
portainer container logs 1 abc123def456 --lines 100
```

Options:
- `--lines` - Number of log lines (default: 50)

### container stats
Get container stats (CPU, RAM, Network).
```bash
portainer container stats <endpoint> <container_id>
```

### container start/stop/restart
Control container state.
```bash
portainer container start <endpoint> <container_id>
portainer container stop <endpoint> <container_id>
portainer container restart <endpoint> <container_id>
```

## Watch Commands

### watch images
Start image update monitoring.
```bash
portainer watch images --interval 6 --endpoint 1
```

Options:
- `--interval` - Polling interval in hours (default: 12)
- `--endpoint` - Specific endpoint ID (default: all)

### watch status
Show monitoring status.
```bash
portainer watch status
```

## Events Commands

### events start
Listen to events in real-time.
```bash
portainer events start --types container,image --duration 60
```

Options:
- `--endpoint` - Specific endpoint ID (default: all)
- `--types` - Event types comma-separated (default: container)
- `--duration` - Duration in seconds (default: 30)

### events list
Get recent events.
```bash
portainer events list <endpoint>
portainer events list 1 --since 3600
```

Options:
- `--since` - Seconds in the past (default: 3600)

## Health Commands

### health check
Check stack health.
```bash
portainer health check <name>
```

### health all
Check all stacks health.
```bash
portainer health all
```

## System Commands

### system stats
Get overall system statistics.
```bash
portainer system stats
```
