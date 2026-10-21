"""Pull apt history from agents into package_update_events; shape query results."""

import logging
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse, urlunparse

import httpx

from app.core.database import AsyncSessionLocal

from ..db_models import SiteDB
from .db_models import PackageUpdateEventDB
from .repositories import PackageUpdateRepository
from .schemas import PackageUpdateEventResponse

logger = logging.getLogger(__name__)

TIMEOUT = 15.0  # history can be a bit larger than /system on first sync


def build_history_url(system_url: str) -> str | None:
    """Derive the agent's /package-history URL from its /system URL (same host, same auth)."""
    parsed = urlparse(system_url)
    path = parsed.path.rstrip("/")
    if not path.endswith("/system"):
        return None
    return urlunparse(parsed._replace(path=f"{path[: -len('/system')]}/package-history", query="", fragment=""))


def _parse_dt(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def normalize_events(raw_events: Any) -> list[dict[str, Any]]:
    """Validate the agent payload; drop malformed entries and duplicate start times."""
    if not isinstance(raw_events, list):
        return []
    by_start: dict[datetime, dict[str, Any]] = {}
    for raw in raw_events:
        if not isinstance(raw, dict):
            continue
        started_at = _parse_dt(raw.get("started_at"))
        if started_at is None:
            continue
        packages = raw.get("packages")
        requested_by = raw.get("requested_by")
        by_start[started_at] = {
            "started_at": started_at,
            "finished_at": _parse_dt(raw.get("finished_at")),
            "commandline": raw.get("commandline"),
            "requested_by": str(requested_by)[:255] if requested_by else None,
            "automatic": bool(raw.get("automatic", False)),
            "packages": packages if isinstance(packages, dict) else {},
        }
    return list(by_start.values())


class PackageHistorySyncService:
    async def sync_site(self, site: SiteDB) -> int:
        """Fetch events newer than the last stored one and store them. Returns rows inserted."""
        # Local import: service.py imports this module at load time.
        from ..service import _auth_headers, _resolve_url

        if not site.system_url:
            return 0
        history_url = build_history_url(site.system_url)
        if history_url is None:
            logger.debug("Package history skipped for %s: system_url does not end with /system", site.name)
            return 0

        async with AsyncSessionLocal() as db:
            since = await PackageUpdateRepository(db).get_latest_started_at(site.id)

        url, extra_headers = _resolve_url(history_url, site.ip)
        if since is not None and since.tzinfo is None:
            since = since.replace(tzinfo=UTC)  # naive values come back from non-PostgreSQL backends
        params = {"since": since.astimezone(UTC).isoformat()} if since else None
        headers = {**_auth_headers(site.token), **extra_headers}

        async with httpx.AsyncClient(timeout=TIMEOUT, verify=site.verify_ssl) as client:
            resp = await client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            body = resp.json()

        events = normalize_events(body.get("events") if isinstance(body, dict) else None)
        async with AsyncSessionLocal() as db:
            inserted = await PackageUpdateRepository(db).insert_ignore_duplicates(site.id, events)
        if inserted:
            logger.info("Stored %d new package update event(s) for %s", inserted, site.name)
        return inserted


def to_event_response(event: PackageUpdateEventDB, site: SiteDB) -> PackageUpdateEventResponse:
    duration = int((event.finished_at - event.started_at).total_seconds()) if event.finished_at else None
    host_source = site.system_url or site.health_url
    return PackageUpdateEventResponse(
        id=str(event.id),
        siteId=str(site.id),
        siteName=site.name,
        serverLabel=site.server_label,
        host=urlparse(host_source).hostname if host_source else None,
        startedAt=event.started_at,
        finishedAt=event.finished_at,
        durationSeconds=duration,
        commandline=event.commandline,
        requestedBy=event.requested_by,
        automatic=event.automatic,
        packages=event.packages or {},
    )
