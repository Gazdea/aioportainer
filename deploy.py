#!/usr/bin/env python3
"""CLI: Deploy stack."""
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

    if len(sys.argv) < 2:
        print("Usage: python stack-list.py")
        print("       python deploy.py <stack-name> [commit-message]")
        sys.exit(1)

    stack_name = sys.argv[1]
    commit_msg = sys.argv[2] if len(sys.argv) > 2 else f"Update stack {stack_name}"

    async with PortainerClient(url=url, token=token) as client:
        manager = StackManager(client)
        result = await manager.deploy(stack_name, commit_msg)

        if result.success:
            print(f"\n✓ {result.message}")
            sys.exit(0)
        else:
            print(f"\n✗ {result.message}")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
