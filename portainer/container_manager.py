"""Container management."""
import asyncio
from typing import Optional

from .client import PortainerClient
from .models import Container, ContainerStats


class ContainerManager:
    """Manage Docker containers."""

    def __init__(self, client: PortainerClient):
        """Initialize container manager."""
        self.client = client

    async def get_containers(
        self,
        endpoint_id: str,
        all_containers: bool = True,
        stack_name: str = None,
    ) -> list[Container]:
        """Get containers from endpoint, optionally filtered by stack."""
        raw = await self.client.get_containers(endpoint_id, all_containers)
        containers = []

        for c in raw:
            labels = c.get("Labels", {})
            stack_namespace = labels.get("com.docker.stack.namespace", "")
            compose_project = labels.get("com.docker.compose.project", "")

            # Filter by stack if specified
            if stack_name and stack_name not in [stack_namespace, compose_project]:
                continue

            containers.append(Container(
                id=c.get("Id", ""),
                name=c.get("Names", [""])[0].lstrip("/"),
                image=c.get("Image", ""),
                image_id=c.get("ImageID", ""),
                state=c.get("State", ""),
                status=c.get("Status", ""),
                labels=labels,
                ports=c.get("Ports", {}),
                endpoint_id=int(endpoint_id),
            ))
        return containers

    async def get_container(self, endpoint_id: str, container_id: str) -> Optional[Container]:
        """Get specific container."""
        containers = await self.get_containers(endpoint_id, all_containers=True)
        for c in containers:
            if c.id == container_id or c.name == container_id:
                return c
        return None

    async def get_logs(
        self,
        endpoint_id: str,
        container_id: str,
        lines: int = 50,
    ) -> str:
        """Get container logs."""
        return await self.client.get_container_logs(endpoint_id, container_id, lines)

    async def get_stats(
        self,
        endpoint_id: str,
        container_id: str,
    ) -> ContainerStats:
        """Get container resource stats."""
        raw = await self.client.get_container_stats(endpoint_id, container_id)

        # Parse CPU
        cpu = raw.get("cpu_stats", {})
        precpu = raw.get("precpu_stats", {})
        cpu_delta = cpu.get("cpu_usage", {}).get("total_usage", 0) - precpu.get("cpu_usage", {}).get("total_usage", 0)
        system_delta = cpu.get("system_cpu_usage", 0) - precpu.get("system_cpu_usage", 0)
        num_cpus = cpu.get("online_cpus", 1)
        cpu_percent = 0.0
        if system_delta > 0:
            cpu_percent = (cpu_delta / system_delta) * num_cpus * 100.0

        # Parse Memory
        mem = raw.get("memory_stats", {})
        memory_usage = mem.get("usage", 0)
        memory_limit = mem.get("limit", 1)
        memory_percent = (memory_usage / memory_limit) * 100.0 if memory_limit > 0 else 0

        # Parse Networks
        networks = raw.get("networks", {})
        network_rx = 0
        network_tx = 0
        for net in networks.values():
            network_rx += net.get("rx_bytes", 0)
            network_tx += net.get("tx_bytes", 0)

        # Parse Block I/O
        blkio = raw.get("blkio_stats", {}).get("io_service_bytes_recursive", [])
        block_read = 0
        block_write = 0
        for blk in blkio:
            if blk.get("op") == "read":
                block_read += blk.get("value", 0)
            elif blk.get("op") == "write":
                block_write += blk.get("value", 0)

        return ContainerStats(
            container_id=container_id,
            cpu_percent=round(cpu_percent, 2),
            memory_usage=memory_usage,
            memory_limit=memory_limit,
            memory_percent=round(memory_percent, 2),
            network_rx=network_rx,
            network_tx=network_tx,
            block_read=block_read,
            block_write=block_write,
        )

    async def start(self, endpoint_id: str, container_id: str):
        """Start container."""
        await self.client.start_container(endpoint_id, container_id)

    async def stop(self, endpoint_id: str, container_id: str):
        """Stop container."""
        await self.client.stop_container(endpoint_id, container_id)

    async def restart(self, endpoint_id: str, container_id: str):
        """Restart container."""
        await self.client.restart_container(endpoint_id, container_id)

    async def restart_not_running(self, endpoint_id: str) -> int:
        """Restart all stopped containers on endpoint."""
        containers = await self.get_containers(endpoint_id, all_containers=True)
        restarted = 0
        for c in containers:
            if not c.is_running:
                print(f"Restarting {c.name}...")
                await self.restart(endpoint_id, c.id)
                restarted += 1
        return restarted

    async def get_stack_containers(self, endpoint_id: str, stack_name: str) -> list[Container]:
        """Get all containers for a stack."""
        return await self.get_containers(endpoint_id, stack_name=stack_name)

    async def check_container_health(
        self,
        endpoint_id: str,
        container_id: str,
    ) -> dict:
        """Check container health status."""
        container = await self.get_container(endpoint_id, container_id)
        if not container:
            return {"status": "not_found", "container": None}

        # Get latest stats
        stats = await self.get_stats(endpoint_id, container_id)

        return {
            "status": "healthy" if container.is_running else "unhealthy",
            "container": container,
            "stats": stats,
        }

    async def monitor_stack(
        self,
        stack_name: str,
        check_interval: int = 30,
        on_error=None,
    ) -> None:
        """Monitor stack containers continuously."""
        from .stack_manager import StackManager

        sm = StackManager(self.client)

        stack = await sm.get_stack(stack_name)
        if not stack:
            print(f"Stack {stack_name} not found")
            return

        print(f"Monitoring stack: {stack_name} (Endpoint: {stack.endpoint_id})")

        while True:
            containers = await self.get_containers(
                str(stack.endpoint_id),
                stack_name=stack_name
            )

            print(f"\n=== Stack: {stack_name} ===")

            for c in containers:
                stats = await self.get_stats(str(stack.endpoint_id), c.id)
                health = "✓" if c.is_running else "✗"
                print(f"  {health} {c.name}: {c.state} | CPU: {stats.cpu_percent}% | Mem: {stats.memory_usage_mb:.1f}MB")

                if not c.is_running and on_error:
                    logs = await self.get_logs(str(stack.endpoint_id), c.id, 20)
                    await on_error(c, logs)

            if not containers:
                print("  No containers found")

            await asyncio.sleep(check_interval)
