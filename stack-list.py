#!/usr/bin/env python3
"""CLI: List all stacks."""
import asyncio
import os
import sys

# Add scripts to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from portainer import PortainerClient, StackManager


async def main():
    url = os.getenv("PORTAINER_URL", "https://gaz-linux:9443")
    token = os.getenv("PORTAINER_TOKEN", "")

    if not token:
        print("Error: PORTAINER_TOKEN is required")
        sys.exit(1)

    async with PortainerClient(url=url, token=token) as client:
        manager = StackManager(client)
        stacks = await manager.list_stacks()

        print("ID    NAME                    STATUS    ENDPOINT    STATE")
        print("---   ----                    ------    --------    -----")

        for s in stacks:
            status_emoji = "✓" if s.is_active else "✗" if s.is_error else "○"
            print(f"{s.id:<4}  {s.name:<22} {s.status_text:<8} {s.endpoint_id:<9} {status_emoji} {s.state}")

        print(f"\n{len(stacks)} stacks total")
        print("\nStatus: 1=Active ✓, 2=Inactive, 3=Removing, 4=Error ✗")


if __name__ == "__main__":
    asyncio.run(main())
