---
name: portainer-git
description: Git workflow for Portainer stack deployment - commit, push, and deploy integration
license: MIT
compatibility: opencode
metadata:
  audience: maintainers
  workflow: portainer
---

## Overview

Git integration for Portainer stack deployment. Handles commit message generation, automatic git operations, pull/rebase, and deployment triggering.

## Git Workflow (StackManager)

### Deploy Process

1. **Fetch** - `git fetch origin` to check remote status
2. **Check behind** - `git rev-list --count HEAD..origin/main`
3. **Pull if needed** - `git pull --rebase origin main`
4. **Commit** - `git add -A && git commit -m "message"`
5. **Push** - `git push origin main`
6. **Trigger Redeploy** - Call Portainer API
7. **Monitor** - Poll until stack status = Active (1) or Error (4)

### Implementation

```python
class StackManager:
    async def deploy(
        self,
        name: str,
        commit_message: str = None,
        poll_interval: int = 5,
        max_retries: int = 24,
    ) -> StackDeployment:
        """Deploy stack: commit → push → redeploy → monitor."""
        commit_msg = commit_message or f"Update stack {name}"
        
        stack = await self.get_stack(name)
        
        # Git operations
        await self._git_commit_push(commit_msg)
        
        # Trigger Portainer redeploy
        await self.client.redeploy_stack(stack.id, stack.endpoint_id)
        
        # Monitor deployment
        for attempt in range(max_retries):
            await asyncio.sleep(poll_interval)
            status = await self.client.get_stack_details(stack.id, stack.endpoint_id)
            if status == 1:  # Active
                return success
            if status == 4:  # Error
                return failure

    async def _git_commit_push(self, message: str):
        """Git commit and push with rebase."""
        # Fetch and check if behind
        subprocess.run(["git", "fetch", "origin"], capture_output=True)
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD..origin/main"],
            capture_output=True, text=True
        )
        behind = int(result.stdout.strip() or 0)

        if behind > 0:
            subprocess.run(
                ["git", "pull", "--rebase", "origin", "main"],
                capture_output=True, text=True
            )

        # Add and commit
        subprocess.run(["git", "add", "-A"], capture_output=True)
        result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True, text=True
        )

        # Push
        subprocess.run(
            ["git", "push", "origin", "main"],
            capture_output=True, text=True
        )
```

## CLI Integration

```bash
# Deploy stack (commit + push + redeploy + monitor)
portainer stack deploy mystack "Update configuration"

# Options
portainer stack deploy mystack "msg" --poll-interval 5 --max-retries 24
```

## Manual Git Commands

```bash
# Check status
git status

# Add all changes
git add -A

# Commit with message
git commit -m "Update stack mystack"

# Push to remote
git push origin main

# Fetch and rebase
git fetch origin
git pull --rebase origin main

# View git log
git log --oneline -10

# Check current branch
git branch

# Check behind/ahead
git rev-list --count HEAD..origin/main
git rev-list --count origin/main..HEAD
```

## Commit Message Format

Standard format: `{action} {component}: {description}`

Examples:
- `deploy mystack: update configuration`
- `fix nginx: fix upstream proxy`
- `update db: add new environment variable`
- `deploy api: update to v2.1.0`

## Adding Git Features

1. Use `subprocess.run()` for git commands
2. Always capture output for debugging
3. Handle errors gracefully
4. Return structured results
5. Run `ruff check` and `pytest` before committing
