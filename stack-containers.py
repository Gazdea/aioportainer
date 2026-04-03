#!/usr/bin/env python3
"""CLI: Get stack containers."""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from portainer import PortainerClient, StackManager, ContainerManager


async def main():
    url = os.getenv("PORTAINER_URL", "https://gaz-linux:9443")
    token = os.getenv("PORTAINER_TOKEN", "")

    if not token:
        print("Error: PORTAINER_TOKEN is required")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python stack-containers.py <stack-name>")
        sys.exit(1)

    stack_name = sys.argv[1]

    async with PortainerClient(url=url, token=token) as client:
        cm = ContainerManager(client)
        sm = StackManager(client)

        stack = await sm.get_stack(stack_name)
        if not stack:
            print(f"Stack '{stack_name}' not found")
            sys.exit(1)

        containers = await sm.get_stack_containers(stack_name)

        print(f"=== Stack: {stack_name} (Endpoint: {stack.endpoint_id}) ===\n")
        print("NAME                    STATE     STATUS                      IMAGE")
        print("----                    -----     ------                      -----")

        for c in containers:
            status_emoji = "✓" if c.is_running else "✗"
            print(f"{c.name:<22} {c.state:<9} {c.status:<26} {c.image}")

        print(f"\n{len(containers)} containers")


if __name__ == "__main__":
    asyncio.run(main())
