#!/usr/bin/env python3
"""CLI: Get container logs."""
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
        print("Usage: python container-logs.py <endpoint-id> <container-id> [lines]")
        sys.exit(1)

    endpoint_id = sys.argv[1]
    container_id = sys.argv[2]
    lines = int(sys.argv[3]) if len(sys.argv) > 3 else 50

    async with PortainerClient(url=url, token=token) as client:
        cm = ContainerManager(client)
        logs = await cm.get_logs(endpoint_id, container_id, lines)
        print(logs or "(no logs)")


if __name__ == "__main__":
    asyncio.run(main())
