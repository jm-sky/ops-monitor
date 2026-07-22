"""Background poller — asyncio task that calls MonitorService on schedule."""

import asyncio
import logging
from datetime import UTC, datetime, timedelta

from app.core.config import settings

from .service import MonitorService

logger = logging.getLogger(__name__)

CHECK_INTERVAL = settings.monitor.check_interval_seconds
LIVE_POLL_INTERVAL = settings.monitor.live_poll_interval_seconds
LIVE_MODE_TTL = settings.monitor.live_mode_ttl_seconds

# Module-level live mode expiry (set by heartbeat endpoint)
_live_mode_until: datetime | None = None


def activate_live_mode() -> None:
    """Extend live mode for LIVE_MODE_TTL seconds from now."""
    global _live_mode_until
    _live_mode_until = datetime.now(UTC) + timedelta(seconds=LIVE_MODE_TTL)


def is_live_mode_active() -> bool:
    return _live_mode_until is not None and datetime.now(UTC) < _live_mode_until


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
                await self._service.poll_due_sites(self._last_polled, live=is_live_mode_active())
            except Exception as e:
                logger.error("Poller iteration error: %s", e, exc_info=True)
            await asyncio.sleep(CHECK_INTERVAL)


# Module-level singleton used by the app factory
poller = PollerScheduler()
