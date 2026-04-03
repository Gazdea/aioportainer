"""Image watcher for monitoring container image updates."""
import asyncio
import datetime
import logging
from dataclasses import dataclass
from typing import Callable, Optional

from .client import PortainerClient

logger = logging.getLogger(__name__)


@dataclass
class ImageUpdateStatus:
    """Image update status."""

    update_available: bool = False
    local_digest: Optional[str] = None
    registry_digest: Optional[str] = None


@dataclass
class ImageWatcherResult:
    """Image watcher result."""

    endpoint_id: int
    container_id: str
    container_name: str
    image: str
    status: Optional[ImageUpdateStatus] = None


class ImageWatcher:
    """Monitor Docker containers for available image updates."""

    def __init__(
        self,
        client: PortainerClient,
        interval: datetime.timedelta = None,
        endpoint_id: Optional[int] = None,
        debug: bool = False,
    ):
        """Initialize image watcher.

        Args:
            client: PortainerClient instance
            interval: Polling interval (default: 12 hours)
            endpoint_id: Specific endpoint to monitor, None for all
            debug: Enable debug logging
        """
        self.client = client
        self.interval = interval or datetime.timedelta(hours=12)
        self.endpoint_id = endpoint_id
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._callbacks: list[Callable] = []
        self._results: dict[tuple[int, str], ImageWatcherResult] = {}
        self._last_check: Optional[float] = None

        if debug:
            logging.basicConfig(level=logging.DEBUG)

    @property
    def results(self) -> dict[tuple[int, str], ImageWatcherResult]:
        """Get current results."""
        return self._results

    @property
    def last_check(self) -> Optional[float]:
        """Get last check timestamp."""
        return self._last_check

    def register_callback(self, callback: Callable) -> None:
        """Register callback for results."""
        self._callbacks.append(callback)

    def unregister_callback(self, callback: Callable) -> None:
        """Unregister callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    async def _poll_once(self) -> None:
        """Poll for image updates once."""
        logger.debug("Starting image poll")

        endpoints = await self.client.get_endpoints()
        for ep in endpoints:
            ep_id = ep.get("Id")
            if self.endpoint_id and ep_id != self.endpoint_id:
                continue

            try:
                containers = await self.client.get_containers(str(ep_id), all_containers=True)
                for c in containers:
                    await self._check_container(ep_id, c)
            except Exception as e:
                logger.error(f"Error polling endpoint {ep_id}: {e}")

        self._last_check = asyncio.get_event_loop().time()
        logger.debug(f"Image poll completed, found {len(self._results)} containers")

    async def _check_container(self, endpoint_id: int, container: dict) -> None:
        """Check a single container for image updates."""
        container_id = container.get("Id", "")
        container_name = container.get("Names", [""])[0].lstrip("/")
        image = container.get("Image", "")
        image_id = container.get("ImageID", "")

        if not image:
            return

        try:
            local_digest = self._extract_digest(image_id)

            registry_image = image.split(":")[0] if ":" in image else image
            registry_tag = image.split(":")[1] if ":" in image else "latest"

            registry_digest = await self._get_registry_digest(endpoint_id, registry_image, registry_tag)

            update_available = False
            if local_digest and registry_digest:
                update_available = local_digest != registry_digest

            result = ImageWatcherResult(
                endpoint_id=endpoint_id,
                container_id=container_id,
                container_name=container_name,
                image=image,
                status=ImageUpdateStatus(
                    update_available=update_available,
                    local_digest=local_digest,
                    registry_digest=registry_digest,
                ),
            )

            key = (endpoint_id, container_id)
            self._results[key] = result

            for callback in self._callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(result)
                    else:
                        callback(result)
                except Exception as e:
                    logger.error(f"Callback error: {e}")

        except Exception as e:
            logger.error(f"Error checking container {container_id}: {e}")

    def _extract_digest(self, image_id: str) -> Optional[str]:
        """Extract digest from image ID."""
        if not image_id:
            return None
        if image_id.startswith("sha256:"):
            return image_id
        return None

    async def _get_registry_digest(
        self, endpoint_id: int, image: str, tag: str
    ) -> Optional[str]:
        """Get image digest from registry."""
        try:
            registries = await self.client.get_registries()

            registry_url = "docker.io"
            for reg in registries:
                if image.startswith(reg.get("URL", "").replace("https://", "").replace("http://", "")):
                    registry_url = reg.get("URL", "").replace("https://", "").replace("http://", "")
                    break

            pull_result = await self.client.pull_image(
                str(endpoint_id), image, registry=registry_url, tag=tag
            )

            if pull_result:
                return image

        except Exception as e:
            logger.debug(f"Could not get registry digest for {image}: {e}")

        return None

    async def _run(self) -> None:
        """Run the watcher loop."""
        while self._running:
            try:
                await self._poll_once()
            except Exception as e:
                logger.error(f"Poll error: {e}")

            await asyncio.sleep(self.interval.total_seconds())

    def start(self) -> None:
        """Start the watcher."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run())
        logger.info(f"ImageWatcher started with interval {self.interval}")

    def stop(self) -> None:
        """Stop the watcher."""
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("ImageWatcher stopped")
