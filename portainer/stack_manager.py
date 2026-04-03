"""Stack management."""
import asyncio
import subprocess
from typing import Optional

from .client import PortainerClient
from .models import Container, Stack, StackDeployment


class StackManager:
    """Manage Portainer stacks."""

    def __init__(self, client: PortainerClient):
        """Initialize stack manager."""
        self.client = client

    async def list_stacks(self) -> list[Stack]:
        """List all stacks."""
        raw_stacks = await self.client.get_stacks()
        stacks = []
        for s in raw_stacks:
            git_config = s.get("GitConfig", {})
            stacks.append(Stack(
                id=s.get("Id", 0),
                name=s.get("Name", ""),
                endpoint_id=s.get("EndpointId", 0),
                status=s.get("Status", 0),
                state=s.get("State", ""),
                project_path=s.get("ProjectPath", ""),
                git_url=git_config.get("URL", ""),
                git_reference=git_config.get("ReferenceName", ""),
                git_config_path=git_config.get("ConfigFilePath", ""),
                created_by=s.get("CreatedBy", ""),
                creation_date=s.get("CreationDate", 0),
                update_date=s.get("UpdateDate", 0),
            ))
        return stacks

    async def get_stack(self, name: str) -> Optional[Stack]:
        """Get stack by name."""
        raw = await self.client.get_stack(name)
        if not raw:
            return None

        git_config = raw.get("GitConfig", {})
        return Stack(
            id=raw.get("Id", 0),
            name=raw.get("Name", ""),
            endpoint_id=raw.get("EndpointId", 0),
            status=raw.get("Status", 0),
            state=raw.get("State", ""),
            project_path=raw.get("ProjectPath", ""),
            git_url=git_config.get("URL", ""),
            git_reference=git_config.get("ReferenceName", ""),
            git_config_path=git_config.get("ConfigFilePath", ""),
            created_by=raw.get("CreatedBy", ""),
            creation_date=raw.get("CreationDate", 0),
            update_date=raw.get("UpdateDate", 0),
        )

    async def deploy(
        self,
        name: str,
        commit_message: str = None,
        poll_interval: int = 5,
        max_retries: int = 24,
    ) -> StackDeployment:
        """Deploy stack: commit → push → redeploy → monitor."""
        commit_msg = commit_message or f"Update stack {name}"

        # Find stack
        stack = await self.get_stack(name)
        if not stack:
            return StackDeployment(
                stack=Stack(id=0, name=name, endpoint_id=0, status=0),
                success=False,
                message=f"Stack '{name}' not found",
            )

        print(f"=== Deploying stack: {name} ===")
        print(f"Stack ID: {stack.id} (Endpoint: {stack.endpoint_id})")
        print(f"Current status: {stack.status_text}\n")

        # Git: commit and push
        print("=== Git: Commit and Push ===")
        await self._git_commit_push(commit_msg)

        # Portainer: trigger redeploy
        print("\n=== Portainer: Trigger Redeploy ===")
        await self.client.redeploy_stack(stack.id, stack.endpoint_id)
        print("Redeploy triggered")

        # Monitor
        print(f"\n=== Monitoring (every {poll_interval}s, max {max_retries} attempts) ===\n")

        last_status = 0
        for attempt in range(1, max_retries + 1):
            await asyncio.sleep(poll_interval)

            try:
                details = await self.client.get_stack_details(stack.id, stack.endpoint_id)
                last_status = details.get("Status", 0)
                print(f"[{attempt}/{max_retries}] Status: {last_status}")

                if last_status == 1:  # Active
                    return StackDeployment(
                        stack=stack,
                        success=True,
                        message=f"Stack {name} deployed successfully",
                    )

                if last_status == 4:  # Error
                    return StackDeployment(
                        stack=stack,
                        success=False,
                        message=f"Stack {name} deployment failed",
                    )
            except Exception as e:
                print(f"[{attempt}/{max_retries}] Error: {e}")

        return StackDeployment(
            stack=stack,
            success=False,
            message=f"Timeout after {poll_interval * max_retries}s",
        )

    async def _git_commit_push(self, message: str):
        """Git commit and push."""
        # Fetch and check if behind
        subprocess.run(["git", "fetch", "origin"], capture_output=True)
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD..origin/main"],
            capture_output=True, text=True
        )
        behind = int(result.stdout.strip() or 0)

        if behind > 0:
            print(f"Local is behind remote by {behind} commits, pulling...")
            result = subprocess.run(
                ["git", "pull", "--rebase", "origin", "main"],
                capture_output=True, text=True
            )
            print(result.stdout or result.stderr)

        # Commit
        subprocess.run(["git", "add", "-A"], capture_output=True)
        result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("(No changes to commit)")

        # Push
        result = subprocess.run(
            ["git", "push", "origin", "main"],
            capture_output=True, text=True
        )
        print(result.stdout or result.stderr)

    async def get_stack_containers(self, name: str) -> list[Container]:
        """Get containers for a stack."""
        stack = await self.get_stack(name)
        if not stack:
            return []

        raw_containers = await self.client.get_containers(str(stack.endpoint_id))
        containers = []
        for c in raw_containers:
            labels = c.get("Labels", {})
            stack_namespace = labels.get("com.docker.stack.namespace", "")
            compose_project = labels.get("com.docker.compose.project", "")

            if stack_namespace == name or compose_project == name:
                containers.append(Container(
                    id=c.get("Id", ""),
                    name=c.get("Names", [""])[0].lstrip("/"),
                    image=c.get("Image", ""),
                    image_id=c.get("ImageID", ""),
                    state=c.get("State", ""),
                    status=c.get("Status", ""),
                    labels=labels,
                    ports=c.get("Ports", {}),
                    endpoint_id=stack.endpoint_id,
                ))
        return containers
