"""Monitor service — polls sites via httpx, stores snapshots."""

import logging
from datetime import UTC, datetime
from typing import Any

import httpx

from app.core.database import AsyncSessionLocal

from .alerts.dispatcher import dispatch_if_changed
from .db_models import SiteDB
from .repositories import SnapshotRepository, SiteRepository

logger = logging.getLogger(__name__)

TIMEOUT = 10.0  # seconds per request

_STATUS_MAP = {
    "healthy": "ok",
    "up": "ok",
    "pass": "ok",
    "ok": "ok",
    "degraded": "degraded",
    "warn": "degraded",
    "warning": "degraded",
    "down": "failed",
    "error": "failed",
    "fail": "failed",
    "failed": "failed",
}


def _normalize_status(raw: str | None) -> str:
    if not raw:
        return "ok"
    return _STATUS_MAP.get(str(raw).lower(), raw)


class MonitorService:
    async def poll_due_sites(self, last_polled: dict[str, dict[str, datetime]]) -> None:
        """Check all enabled sites and poll those overdue for their next check."""
        async with AsyncSessionLocal() as db:
            repo = SiteRepository(db)
            sites = await repo.get_enabled()

        now = datetime.now(UTC)

        for site in sites:
            site_key = str(site.id)
            site_times = last_polled.setdefault(site_key, {})

            if site.health_url:
                last = site_times.get("health")
                if last is None or (now - last).total_seconds() >= site.polling_health:
                    try:
                        await self._poll_health(site)
                    except Exception as e:
                        logger.error("Health poll failed for %s: %s", site.name, e)
                    site_times["health"] = now

            if site.system_url:
                last = site_times.get("system")
                if last is None or (now - last).total_seconds() >= site.polling_system:
                    try:
                        await self._poll_system(site)
                    except Exception as e:
                        logger.error("System poll failed for %s: %s", site.name, e)
                    site_times["system"] = now

    async def poll_site_now(self, site: SiteDB) -> dict[str, Any]:
        """Immediately poll a site and return snapshot data (on-demand refresh)."""
        results: dict[str, Any] = {}
        if site.health_url:
            snap = await self._poll_health(site)
            results["health"] = snap.to_response()
        if site.system_url:
            snap = await self._poll_system(site)
            results["system"] = snap.to_response()
        return results

    async def _poll_health(self, site: SiteDB) -> Any:
        headers = _auth_headers(site.token)
        raw_data = None
        error = None
        status = None

        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                resp = await client.get(site.health_url, headers=headers)  # type: ignore[arg-type]
                resp.raise_for_status()
                try:
                    raw_data = resp.json()
                except Exception:
                    raise ValueError(
                        f"Non-JSON response (content-type: {resp.headers.get('content-type', 'unknown')})"
                    )
                if not isinstance(raw_data, dict):
                    raise ValueError(
                        f"Expected JSON object, got {type(raw_data).__name__}"
                    )
                status = _normalize_status(raw_data.get("status"))
        except httpx.TimeoutException:
            error = "Connection timeout"
            status = "failed"
        except httpx.HTTPStatusError as e:
            error = f"HTTP {e.response.status_code}"
            status = "failed"
        except Exception as e:
            error = str(e)
            status = "failed"

        logger.debug("Health poll %s → status=%s error=%s", site.name, status, error)

        async with AsyncSessionLocal() as db:
            repo = SnapshotRepository(db)
            snap = await repo.create(site.id, "health", raw_data, error, status)
            await repo.cleanup_old(site.id, "health")

        await dispatch_if_changed(site, snap)
        return snap

    async def _poll_system(self, site: SiteDB) -> Any:
        headers = _auth_headers(site.token)
        raw_data = None
        error = None
        status = None

        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                resp = await client.get(site.system_url, headers=headers)  # type: ignore[arg-type]
                resp.raise_for_status()
                raw_data = resp.json()
                reboot_req = raw_data.get("reboot_required", False)
                system_state = raw_data.get("system_state", "up_to_date")
                status = "reboot_required" if reboot_req else system_state
        except httpx.TimeoutException:
            error = "Connection timeout"
            status = "failed"
        except httpx.HTTPStatusError as e:
            error = f"HTTP {e.response.status_code}"
            status = "failed"
        except Exception as e:
            error = str(e)
            status = "failed"

        logger.debug("System poll %s → status=%s error=%s", site.name, status, error)

        async with AsyncSessionLocal() as db:
            repo = SnapshotRepository(db)
            snap = await repo.create(site.id, "system", raw_data, error, status)
            await repo.cleanup_old(site.id, "system")

        await dispatch_if_changed(site, snap)
        return snap


def _auth_headers(token: str | None) -> dict[str, str]:
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}
