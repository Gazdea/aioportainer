#!/usr/bin/env python3
"""CLI: Get container stats (CPU, RAM, Network, etc)."""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from portainer import PortainerClient, ContainerManager


async def main():
    url = os.getenv("PORTAINER_URL", "https://gaz-linux:9443")
    token = os.getenv("PORTAINER_TOKEN", "")

    if not token:
        print("Error: PORTAINER_TOKEN is required")
        sys.exit(1)

    if len(sys.argv) < 3:
        print("Usage: python container-stats.py <endpoint-id> <container-id>")
        sys.exit(1)

    endpoint_id = sys.argv[1]
    container_id = sys.argv[2]

    async with PortainerClient(url=url, token=token) as client:
        cm = ContainerManager(client)
        stats = await cm.get_stats(endpoint_id, container_id)

        print(f"=== Container: {container_id[:12]} ===")
        print(f"CPU:        {stats.cpu_percent}%")
        print(f"Memory:     {stats.memory_usage_mb:.1f}MB / {stats.memory_limit_mb:.1f}MB ({stats.memory_percent}%)")
        print(f"Network RX: {stats.network_rx / 1024:.1f}KB")
        print(f"Network TX: {stats.network_tx / 1024:.1f}KB")
        print(f"Block Read:  {stats.block_read / 1024:.1f}KB")
        print(f"Block Write: {stats.block_write / 1024:.1f}KB")


if __name__ == "__main__":
    asyncio.run(main())
