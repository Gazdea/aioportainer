"""Health monitoring."""
import asyncio
import datetime
from typing import Callable

from .client import PortainerClient
from .container_manager import ContainerManager
from .models import Container
from .stack_manager import StackManager


class HealthMonitor:
    """Health monitoring for stacks and containers."""

    def __init__(self, client: PortainerClient):
        """Initialize health monitor."""
        self.client = client
        self.stack_manager = StackManager(client)
        self.container_manager = ContainerManager(client)
        self._monitoring = False

    async def check_stack_health(self, stack_name: str) -> dict:
        """Check health of entire stack."""
        stack = await self.stack_manager.get_stack(stack_name)
        if not stack:
            return {"status": "not_found", "stack": None}

        containers = await self.stack_manager.get_stack_containers(stack_name)
        healthy_count = sum(1 for c in containers if c.is_running)

        return {
            "status": "healthy" if stack.is_active and healthy_count == len(containers) else "unhealthy",
            "stack": stack,
            "containers": containers,
            "healthy_count": healthy_count,
            "total_count": len(containers),
        }

    async def check_all_stacks(self) -> list[dict]:
        """Check health of all stacks."""
        stacks = await self.stack_manager.list_stacks()
        results = []

        for stack in stacks:
            result = await self.check_stack_health(stack.name)
            results.append(result)

        return results

    async def wait_for_stack(
        self,
        stack_name: str,
        timeout: int = 120,
        poll_interval: int = 5,
    ) -> bool:
        """Wait for stack to become healthy."""
        start_time = datetime.datetime.now()
        elapsed = 0

        while elapsed < timeout:
            health = await self.check_stack_health(stack_name)

            if health["status"] == "healthy":
                return True

            if health["status"] == "unhealthy":
                stack = health["stack"]
                if stack and stack.is_error:
                    return False

            await asyncio.sleep(poll_interval)
            elapsed = (datetime.datetime.now() - start_time).seconds

        return False

    async def monitor_loop(
        self,
        stack_names: list[str] = None,
        check_interval: int = 60,
        on_change: Callable[[str, dict], None] = None,
        on_error: Callable[[str, Container, str], None] = None,
    ) -> None:
        """Continuous monitoring loop."""
        self._monitoring = True
        previous_state = {}

        if stack_names is None:
            stacks = await self.stack_manager.list_stacks()
            stack_names = [s.name for s in stacks]

        print(f"Starting health monitor for: {', '.join(stack_names)}")
        print(f"Check interval: {check_interval}s\n")

        while self._monitoring:
            for stack_name in stack_names:
                health = await self.check_stack_health(stack_name)
                current_state = health["status"]

                # Check for state change
                prev_state = previous_state.get(stack_name)
                if prev_state and prev_state != current_state:
                    print(f"[{stack_name}] State changed: {prev_state} → {current_state}")
                    if on_change:
                        on_change(stack_name, health)

                # Check for errors
                if current_state == "unhealthy":
                    stack = health.get("stack")
                    if stack and stack.is_error:
                        print(f"[{stack_name}] ERROR: Stack status is Error")
                        if on_error:
                            for container in health.get("containers", []):
                                if not container.is_running:
                                    logs = await self.container_manager.get_logs(
                                        str(stack.endpoint_id),
                                        container.id,
                                        30
                                    )
                                    on_error(stack_name, container, logs)

                previous_state[stack_name] = current_state

                # Print status
                status_emoji = "✓" if current_state == "healthy" else "✗"
                total = health.get("total_count", 0)
                healthy = health.get("healthy_count", 0)
                print(f"{status_emoji} {stack_name}: {current_state} ({healthy}/{total} containers)")

            await asyncio.sleep(check_interval)

    def stop_monitoring(self):
        """Stop monitoring loop."""
        self._monitoring = False

    async def get_system_stats(self) -> dict:
        """Get overall system statistics."""
        endpoints = await self.client.get_endpoints()
        all_stacks = await self.stack_manager.list_stacks()
        all_containers = []

        for ep in endpoints:
            ep_id = str(ep.get("Id"))
            containers = await self.container_manager.get_containers(ep_id)
            all_containers.extend(containers)

        running = sum(1 for c in all_containers if c.is_running)
        stopped = len(all_containers) - running
        healthy_stacks = sum(1 for s in all_stacks if s.is_active)
        error_stacks = sum(1 for s in all_stacks if s.is_error)

        return {
            "endpoints": len(endpoints),
            "stacks": {
                "total": len(all_stacks),
                "healthy": healthy_stacks,
                "error": error_stacks,
            },
            "containers": {
                "total": len(all_containers),
                "running": running,
                "stopped": stopped,
            },
        }

    async def create_alert(
        self,
        stack_name: str,
        message: str,
        severity: str = "error",
    ) -> dict:
        """Create alert for stack."""
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "stack": stack_name,
            "message": message,
            "severity": severity,
        }
