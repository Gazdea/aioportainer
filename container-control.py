#!/usr/bin/env python3
"""CLI: Container control (start/stop/restart)."""
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

    if len(sys.argv) < 4:
        print("Usage: python container-control.py <start|stop|restart> <endpoint-id> <container-id>")
        sys.exit(1)

    action = sys.argv[1].lower()
    endpoint_id = sys.argv[2]
    container_id = sys.argv[3]

    if action not in ["start", "stop", "restart"]:
        print(f"Unknown action: {action}")
        sys.exit(1)

    async with PortainerClient(url=url, token=token) as client:
        cm = ContainerManager(client)

        if action == "start":
            await cm.start(endpoint_id, container_id)
            print(f"Started container {container_id[:12]}")
        elif action == "stop":
            await cm.stop(endpoint_id, container_id)
            print(f"Stopped container {container_id[:12]}")
        elif action == "restart":
            await cm.restart(endpoint_id, container_id)
            print(f"Restarted container {container_id[:12]}")


if __name__ == "__main__":
    asyncio.run(main())
