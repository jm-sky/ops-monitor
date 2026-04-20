"""Monitor service — polls sites via httpx, stores snapshots."""

import logging
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse, urlunparse

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
    async def poll_due_sites(
        self,
        last_polled: dict[str, dict[str, datetime]],
        live: bool = False,
    ) -> None:
        """Check all enabled sites and poll those overdue for their next check.

        When *live* is True the effective per-site interval is capped at
        LIVE_POLL_INTERVAL so the dashboard receives fresh data quickly.
        """
        from .scheduler import LIVE_POLL_INTERVAL

        async with AsyncSessionLocal() as db:
            repo = SiteRepository(db)
            sites = await repo.get_enabled()

        now = datetime.now(UTC)

        for site in sites:
            site_key = str(site.id)
            site_times = last_polled.setdefault(site_key, {})

            health_interval = (
                min(site.polling_health, LIVE_POLL_INTERVAL)
                if live
                else site.polling_health
            )
            system_interval = (
                min(site.polling_system, LIVE_POLL_INTERVAL)
                if live
                else site.polling_system
            )

            if site.health_url:
                last = site_times.get("health")
                if last is None or (now - last).total_seconds() >= health_interval:
                    try:
                        await self._poll_health(site)
                    except Exception as e:
                        logger.error("Health poll failed for %s: %s", site.name, e)
                    site_times["health"] = now

            if site.system_url:
                last = site_times.get("system")
                if last is None or (now - last).total_seconds() >= system_interval:
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
        url, extra_headers = _resolve_url(site.health_url, site.ip)  # type: ignore[arg-type]
        headers = {**headers, **extra_headers}
        raw_data = None
        error = None
        status = None

        try:
            async with httpx.AsyncClient(
                timeout=TIMEOUT, verify=site.verify_ssl
            ) as client:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                try:
                    body = resp.json()
                    if isinstance(body, dict):
                        raw_data = body
                        status = _normalize_status(body.get("status"))
                    else:
                        # JSON scalar/array — 2xx is enough to be healthy
                        status = "ok"
                except Exception:
                    # Non-JSON body (plain text, empty) — 2xx means healthy
                    status = "ok"
        except httpx.TimeoutException:
            error = "Connection timeout"
            status = "failed"
        except httpx.HTTPStatusError as e:
            body = e.response.text[:500] if e.response.text else ""
            error = f"HTTP {e.response.status_code}"
            logger.warning("Health poll %s → %s body=%r", site.name, error, body)
            status = "failed"
        except Exception as e:
            error = str(e)
            status = "failed"

        meta_mismatches = _compute_meta_mismatches(raw_data, site.expected_meta)

        logger.debug("Health poll %s → status=%s error=%s", site.name, status, error)

        async with AsyncSessionLocal() as db:
            repo = SnapshotRepository(db)
            snap = await repo.create(
                site.id, "health", raw_data, error, status, meta_mismatches
            )
            await repo.cleanup_old(site.id, "health")

        await dispatch_if_changed(site, snap)
        return snap

    async def _poll_system(self, site: SiteDB) -> Any:
        headers = _auth_headers(site.token)
        url, extra_headers = _resolve_url(site.system_url, site.ip)  # type: ignore[arg-type]
        headers = {**headers, **extra_headers}
        raw_data = None
        error = None
        status = None

        try:
            async with httpx.AsyncClient(
                timeout=TIMEOUT, verify=site.verify_ssl
            ) as client:
                resp = await client.get(url, headers=headers)
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


def _compute_meta_mismatches(
    raw_data: dict | None,
    expected_meta: dict | None,
) -> list[str] | None:
    if not expected_meta:
        return None
    reported_meta: dict = (raw_data or {}).get("meta") or {}
    mismatches = []
    for key, expected in expected_meta.items():
        actual = reported_meta.get(key)
        if actual is None:
            mismatches.append(f"{key}: expected {expected!r}, not present")
        elif actual != expected:
            mismatches.append(f"{key}: expected {expected!r}, got {actual!r}")
    return mismatches if mismatches else None


def _auth_headers(token: str | None) -> dict[str, str]:
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def _resolve_url(url: str, ip: str | None) -> tuple[str, dict[str, str]]:
    if not ip:
        return url, {}
    parsed = urlparse(url)
    original_host = parsed.netloc  # e.g. "bsm-api01.sklodowscy.local:9100"
    port = parsed.port
    new_netloc = f"{ip}:{port}" if port else ip
    new_url = urlunparse(parsed._replace(netloc=new_netloc))
    return new_url, {"Host": original_host}
