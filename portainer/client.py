"""Portainer async HTTP client."""
import os
from typing import Optional

import aiohttp
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PortainerClient:
    """Async Portainer API client."""

    def __init__(
        self,
        url: str = "https://gaz-linux:9443",
        token: Optional[str] = None,
        endpoints: list[str] = None,
        timeout: int = 30,
    ):
        """Initialize client."""
        self.url = url.rstrip("/")
        self.token = token or self._get_token_from_env()
        self.endpoints = endpoints or ["1", "3"]
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None

    def _get_token_from_env(self) -> str:
        """Get token from environment."""
        token = os.getenv("PORTAINER_TOKEN", "")
        if not token:
            raise ValueError("PORTAINER_TOKEN is required")
        return token

    async def __aenter__(self):
        """Async context manager enter."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

    async def connect(self):
        """Create aiohttp session."""
        if self._session is None:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                connector=aiohttp.TCPConnector(ssl=False),
            )

    async def disconnect(self):
        """Close aiohttp session."""
        if self._session:
            await self._session.close()
            self._session = None

    def _headers(self) -> dict:
        """Build request headers."""
        return {"X-API-Key": self.token}

    async def get(self, endpoint: str) -> dict:
        """Execute GET request."""
        url = f"{self.url}/api/{endpoint.lstrip('/')}"
        async with self._session.get(url, headers=self._headers()) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def post(self, endpoint: str, data: dict = None) -> dict:
        """Execute POST request."""
        url = f"{self.url}/api/{endpoint.lstrip('/')}"
        async with self._session.post(url, json=data, headers=self._headers()) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def put(self, endpoint: str, data: dict = None) -> dict:
        """Execute PUT request."""
        url = f"{self.url}/api/{endpoint.lstrip('/')}"
        async with self._session.put(url, json=data, headers=self._headers()) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def delete(self, endpoint: str) -> dict:
        """Execute DELETE request."""
        url = f"{self.url}/api/{endpoint.lstrip('/')}"
        async with self._session.delete(url, headers=self._headers()) as resp:
            resp.raise_for_status()
            return await resp.json()

    # === Endpoints ===

    async def get_endpoints(self) -> list[dict]:
        """Get all endpoints."""
        return await self.get("endpoints")

    async def get_endpoint(self, endpoint_id: str) -> dict:
        """Get endpoint details."""
        return await self.get(f"endpoints/{endpoint_id}")

    # === Stacks ===

    async def get_stacks(self, endpoint_id: str = None) -> list[dict]:
        """Get stacks from endpoint(s)."""
        if endpoint_id:
            return await self.get(f"stacks?endpointId={endpoint_id}")

        all_stacks = []
        for ep in self.endpoints:
            try:
                stacks = await self.get(f"stacks?endpointId={ep}")
                for s in stacks:
                    s["EndpointId"] = int(ep)
                all_stacks.extend(stacks)
            except Exception:
                pass
        return all_stacks

    async def get_stack(self, name: str, endpoint_id: str = None) -> Optional[dict]:
        """Get stack by name."""
        if endpoint_id:
            stacks = await self.get_stacks(endpoint_id)
        else:
            # Search across all endpoints
            for ep in self.endpoints:
                try:
                    stacks = await self.get(f"stacks?endpointId={ep}")
                    for s in stacks:
                        if s.get("Name") == name:
                            # Get actual endpoint from stack details
                            details = await self.get(f"stacks/{s.get('Id')}?endpointId={ep}")
                            s["EndpointId"] = details.get("EndpointId", int(ep))
                            return s
                except Exception:
                    pass
            return None

        for s in stacks:
            if s.get("Name") == name:
                return s
        return None

    async def get_stack_details(self, stack_id: int, endpoint_id: int) -> dict:
        """Get stack details."""
        return await self.get(f"stacks/{stack_id}?endpointId={endpoint_id}")

    async def redeploy_stack(self, stack_id: int, endpoint_id: int, auth: bool = True) -> dict:
        """Trigger stack redeploy from Git."""
        return await self.put(
            f"stacks/{stack_id}/git/redeploy?endpointId={endpoint_id}",
            {"repositoryAuthentication": auth}
        )

    # === Containers ===

    async def get_containers(self, endpoint_id: str, show_all: bool = True) -> list[dict]:
        """Get containers from endpoint."""
        return await self.get(
            f"endpoints/{endpoint_id}/docker/containers/json?all={str(show_all).lower()}"
        )

    async def get_container_logs(self, endpoint_id: str, container_id: str, tail: int = 50) -> str:
        """Get container logs."""
        url = (f"endpoints/{endpoint_id}/docker/containers/{container_id}/logs"
               f"?stdout=true&stderr=true&tail={tail}")
        async with self._session.get(f"{self.url}/api/{url}", headers=self._headers()) as resp:
            if resp.status == 200:
                text = await resp.text()
                return text
            return ""

    async def get_container_stats(self, endpoint_id: str, container_id: str) -> dict:
        """Get container stats."""
        url = f"endpoints/{endpoint_id}/docker/containers/{container_id}/stats?stream=false"
        return await self.get(url)

    async def start_container(self, endpoint_id: str, container_id: str):
        """Start container."""
        url = f"endpoints/{endpoint_id}/docker/containers/{container_id}/start"
        await self.post(url)

    async def stop_container(self, endpoint_id: str, container_id: str):
        """Stop container."""
        url = f"endpoints/{endpoint_id}/docker/containers/{container_id}/stop"
        await self.post(url)

    async def restart_container(self, endpoint_id: str, container_id: str):
        """Restart container."""
        url = f"endpoints/{endpoint_id}/docker/containers/{container_id}/restart"
        await self.post(url)

    # === System ===

    async def get_status(self) -> dict:
        """Get Portainer status."""
        return await self.get("status")

    async def get_version(self) -> dict:
        """Get Portainer version."""
        return await self.get("version")

    # === Users ===

    async def get_users(self) -> list[dict]:
        """Get all users."""
        return await self.get("users")

    async def get_user(self, user_id: int) -> dict:
        """Get user by ID."""
        return await self.get(f"users/{user_id}")

    async def create_user(self, username: str, password: str, role: int = 1) -> dict:
        """Create new user. Role: 1=admin, 2=user."""
        return await self.post("users", {"Username": username, "Password": password, "Role": role})

    async def update_user(self, user_id: int, data: dict) -> dict:
        """Update user."""
        return await self.put(f"users/{user_id}", data)

    async def delete_user(self, user_id: int) -> dict:
        """Delete user."""
        return await self.delete(f"users/{user_id}")

    async def get_user_memberships(self, user_id: int) -> list[dict]:
        """Get user team memberships."""
        return await self.get(f"users/{user_id}/memberships")

    # === Teams ===

    async def get_teams(self) -> list[dict]:
        """Get all teams."""
        return await self.get("teams")

    async def get_team(self, team_id: int) -> dict:
        """Get team by ID."""
        return await self.get(f"teams/{team_id}")

    async def create_team(self, name: str) -> dict:
        """Create new team."""
        return await self.post("teams", {"Name": name})

    async def delete_team(self, team_id: int) -> dict:
        """Delete team."""
        return await self.delete(f"teams/{team_id}")

    async def get_team_members(self, team_id: int) -> list[dict]:
        """Get team members."""
        return await self.get(f"teams/{team_id}/members")

    async def add_team_member(self, team_id: int, user_id: int) -> dict:
        """Add user to team."""
        return await self.post(f"teams/{team_id}/members", {"UserId": user_id})

    async def remove_team_member(self, team_id: int, user_id: int) -> dict:
        """Remove user from team."""
        return await self.delete(f"teams/{team_id}/members/{user_id}")

    # === Registries ===

    async def get_registries(self) -> list[dict]:
        """Get all registries."""
        return await self.get("registries")

    async def get_registry(self, registry_id: int) -> dict:
        """Get registry by ID."""
        return await self.get(f"registries/{registry_id}")

    async def create_registry(
        self,
        name: str,
        registry_type: str,
        url: str = "",
        username: str = "",
        password: str = "",
    ) -> dict:
        """Create new registry."""
        data = {
            "name": name,
            "type": registry_type,
            "url": url,
            "authentication": bool(username),
            "username": username,
            "password": password,
        }
        return await self.post("registries", data)

    async def update_registry(self, registry_id: int, data: dict) -> dict:
        """Update registry."""
        return await self.put(f"registries/{registry_id}", data)

    async def delete_registry(self, registry_id: int) -> dict:
        """Delete registry."""
        return await self.delete(f"registries/{registry_id}")

    # === Images ===

    async def list_images(self, endpoint_id: str) -> list[dict]:
        """List images on endpoint."""
        return await self.get(f"endpoints/{endpoint_id}/docker/images/json")

    async def pull_image(
        self,
        endpoint_id: str,
        image: str,
        registry: str = "",
        tag: str = "latest",
    ) -> dict:
        """Pull image from registry."""
        data = {"image": f"{registry}/{image}:{tag}" if registry else f"{image}:{tag}"}
        return await self.post(f"endpoints/{endpoint_id}/docker/images/create", data)

    async def delete_image(self, endpoint_id: str, image_id: str, force: bool = False) -> dict:
        """Delete image."""
        return await self.delete(
            f"endpoints/{endpoint_id}/docker/images/{image_id}?force={str(force).lower()}"
        )

    async def get_image_digest(self, endpoint_id: str, image: str) -> dict:
        """Get image digest."""
        return await self.get(f"endpoints/{endpoint_id}/docker/images/{image}/json")

    # === Volumes ===

    async def get_volumes(self, endpoint_id: str) -> list[dict]:
        """Get volumes on endpoint."""
        return await self.get(f"endpoints/{endpoint_id}/docker/volumes")

    async def create_volume(self, endpoint_id: str, name: str, driver: str = "local") -> dict:
        """Create volume."""
        return await self.post(
            f"endpoints/{endpoint_id}/docker/volumes/create",
            {"Name": name, "Driver": driver},
        )

    async def delete_volume(self, endpoint_id: str, name: str) -> dict:
        """Delete volume."""
        return await self.delete(f"endpoints/{endpoint_id}/docker/volumes/{name}")

    # === Networks ===

    async def get_networks(self, endpoint_id: str) -> list[dict]:
        """Get networks on endpoint."""
        return await self.get(f"endpoints/{endpoint_id}/docker/networks")

    async def create_network(
        self,
        endpoint_id: str,
        name: str,
        driver: str = "bridge",
        subnet: str = "",
    ) -> dict:
        """Create network."""
        data = {"Name": name, "Driver": driver}
        if subnet:
            data["IPAM"] = {"Config": [{"Subnet": subnet}]}
        return await self.post(f"endpoints/{endpoint_id}/docker/networks/create", data)

    async def delete_network(self, endpoint_id: str, network_id: str) -> dict:
        """Delete network."""
        return await self.delete(f"endpoints/{endpoint_id}/docker/networks/{network_id}")

    # === Settings ===

    async def get_settings(self) -> dict:
        """Get Portainer settings."""
        return await self.get("settings")

    async def update_settings(self, data: dict) -> dict:
        """Update Portainer settings."""
        return await self.put("settings", data)

    # === Docker Hub ===

    async def search_dockerhub(self, term: str, limit: int = 25) -> list[dict]:
        """Search Docker Hub for images."""
        return await self.get(f"dockerhub/search?term={term}&limit={limit}")

    # === Edge Jobs ===

    async def get_edge_jobs(self) -> list[dict]:
        """Get all edge jobs."""
        return await self.get("edge_jobs")

    async def get_edge_job(self, job_id: int) -> dict:
        """Get edge job by ID."""
        return await self.get(f"edge_jobs/{job_id}")

    async def create_edge_job(self, name: str, cron: str = "", paths: list[str] = None) -> dict:
        """Create edge job."""
        data = {"name": name, "cron": cron, "paths": paths or []}
        return await self.post("edge_jobs", data)

    async def delete_edge_job(self, job_id: int) -> dict:
        """Delete edge job."""
        return await self.delete(f"edge_jobs/{job_id}")

    async def execute_edge_job(self, job_id: int, endpoint_ids: list[int]) -> dict:
        """Execute edge job on endpoints."""
        return await self.post(f"edge_jobs/{job_id}/execute", {"endpoints": endpoint_ids})

    # === Events ===

    async def get_recent_events(self, endpoint_id: int, since: int = 3600) -> list[dict]:
        """Get recent Docker events."""
        return await self.get(f"endpoints/{endpoint_id}/docker/events?since={since}")

    async def get_events_stream(self, endpoint_id: int):
        """Stream Docker events (generator)."""
        import contextlib
        url = f"{self.url}/api/endpoints/{endpoint_id}/docker/events"
        async with self._session.get(url, headers=self._headers()) as resp:
            async for line in resp.content:
                if line:
                    with contextlib.suppress(Exception):
                        yield line.decode("utf-8")
