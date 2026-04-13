"""Background poller — asyncio task that calls MonitorService on schedule."""

import asyncio
import logging
from datetime import datetime

from .service import MonitorService

logger = logging.getLogger(__name__)

CHECK_INTERVAL = 10  # seconds between "which sites are due?" iterations


class PollerScheduler:
    def __init__(self) -> None:
        self._task: asyncio.Task | None = None
        self._last_polled: dict[str, dict[str, datetime]] = {}
        self._service = MonitorService()

    def start(self) -> None:
        self._task = asyncio.create_task(self._run(), name="monitor-poller")
        logger.info("Monitor poller started (check interval: %ds)", CHECK_INTERVAL)

    async def stop(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Monitor poller stopped")

    async def _run(self) -> None:
        while True:
            try:
                await self._service.poll_due_sites(self._last_polled)
            except Exception as e:
                logger.error("Poller iteration error: %s", e, exc_info=True)
            await asyncio.sleep(CHECK_INTERVAL)


# Module-level singleton used by the app factory
poller = PollerScheduler()
