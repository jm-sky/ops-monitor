"""Alert dispatcher — detects status changes and fans out to enabled channels."""

import logging
import uuid
from datetime import UTC, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.core.database import AsyncSessionLocal

from ..db_models import SiteDB, SiteSnapshotDB
from .db_models import AlertChannelDB, AlertEventDB
from .repositories import AlertChannelRepository, AlertEventRepository
from .senders.base import AlertPayload, BaseSender
from .senders.email import EmailSender
from .senders.teams import TeamsSender
from .senders.telegram import TelegramSender

logger = logging.getLogger(__name__)

_SENDERS: dict[str, BaseSender] = {
    "teams": TeamsSender(),
    "email": EmailSender(),
    "telegram": TelegramSender(),
}

# alert_type → statuses that trigger an alert
_ALERT_STATUSES: dict[str, set[str]] = {
    "health": {"degraded", "failed"},
    "reboot": {"reboot_required"},
    "updates": {"outdated"},
}

_DEFAULT_TZ = "Europe/Warsaw"


async def dispatch_if_changed(
    site: SiteDB,
    snapshot: SiteSnapshotDB,
) -> None:
    """For each enabled channel: if filters match and dedup/cooldown allow, send."""
    if not snapshot.status:
        return

    alert_type = _alert_type_for_snapshot(snapshot)
    if alert_type is None:
        return

    async with AsyncSessionLocal() as db:
        channel_repo = AlertChannelRepository(db)
        channels = await channel_repo.get_enabled()

    if not channels:
        return

    detail = _build_detail(snapshot)
    payload = AlertPayload(
        site_name=site.name,
        alert_type=alert_type,
        status=snapshot.status,
        detail=detail,
    )

    for channel in channels:
        if not _matches_filters(channel, site, snapshot, alert_type):
            continue
        async with AsyncSessionLocal() as db:
            event_repo = AlertEventRepository(db)
            last_event = await event_repo.get_last_for_channel(channel.id, site.id, alert_type)
        cooldown = _cooldown_minutes(channel)
        if not _should_fire(last_event, snapshot.status, cooldown):
            continue
        await _send_to_channel(channel, payload, site.id, alert_type, snapshot.status)


def _alert_type_for_snapshot(snapshot: SiteSnapshotDB) -> str | None:
    """Map a snapshot to an alert_type, or None if no alert needed."""
    if snapshot.snapshot_type == "health" and snapshot.status in _ALERT_STATUSES["health"]:
        return "health"
    if snapshot.snapshot_type == "system" and snapshot.status in _ALERT_STATUSES["reboot"]:
        return "reboot"

    # security updates: separate alert type for routing
    if snapshot.snapshot_type == "system":
        raw = snapshot.raw_data or {}
        value = raw.get("security_updates")
        if isinstance(value, int) and value > 0:
            return "security_updates"

    if snapshot.snapshot_type == "system" and snapshot.status in _ALERT_STATUSES["updates"]:
        return "updates"
    return None


def _build_detail(snapshot: SiteSnapshotDB) -> str | None:
    if snapshot.error:
        return snapshot.error
    raw = snapshot.raw_data or {}
    if snapshot.snapshot_type == "system":
        parts: list[str] = []
        if raw.get("reboot_reason"):
            parts.append(f"Reboot reason: {raw['reboot_reason']}")
        updates = raw.get("updates_available", 0)
        if updates:
            parts.append(f"Updates available: {updates}")
        return "; ".join(parts) or None
    if snapshot.snapshot_type == "health":
        components = raw.get("components", {})
        failed = [k for k, v in components.items() if isinstance(v, dict) and v.get("status") != "ok"]
        if failed:
            return f"Affected components: {', '.join(failed)}"
    return None


def _matches_filters(
    channel: AlertChannelDB,
    site: SiteDB,
    snapshot: SiteSnapshotDB,
    alert_type: str,
) -> bool:
    """Check whether this channel's filters allow the alert through."""
    filters: dict[str, Any] = channel.filters or {}

    types = filters.get("alert_types") or []
    if types and alert_type not in types:
        return False

    if alert_type == "health":
        min_sev = filters.get("min_health_severity") or "degraded"
        if min_sev == "failed" and snapshot.status != "failed":
            return False

    site_ids_raw = filters.get("site_ids") or []
    tags_raw = filters.get("tags") or []
    if site_ids_raw or tags_raw:
        site_id_str = str(site.id)
        in_sites = site_id_str in site_ids_raw
        site_tags = set(site.tags or [])
        in_tags = bool(set(tags_raw) & site_tags)
        if not (in_sites or in_tags):
            return False

    quiet = filters.get("quiet_hours") or {}
    if quiet.get("enabled") and _is_in_quiet_hours(quiet):
        return False

    return True


def _is_in_quiet_hours(quiet: dict[str, Any], now: datetime | None = None) -> bool:
    """Return True if `now` falls inside the quiet hours window.

    Supports windows that wrap past midnight (e.g. 22:00–07:00).
    """
    start_str = quiet.get("start") or "22:00"
    end_str = quiet.get("end") or "07:00"
    tz_name = quiet.get("timezone") or _DEFAULT_TZ
    try:
        tz = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        tz = ZoneInfo(_DEFAULT_TZ)
    try:
        start = _parse_hhmm(start_str)
        end = _parse_hhmm(end_str)
    except ValueError:
        return False

    current = (now or datetime.now(UTC)).astimezone(tz).time()
    if start == end:
        return False
    if start < end:
        return start <= current < end
    # Wraps past midnight
    return current >= start or current < end


def _parse_hhmm(value: str) -> time:
    hh, mm = value.split(":", 1)
    return time(int(hh), int(mm))


def _cooldown_minutes(channel: AlertChannelDB) -> int | None:
    filters = channel.filters or {}
    raw = filters.get("re_alert_after_minutes")
    if raw is None:
        return None
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return None
    return value if value >= 1 else None


def _should_fire(
    last_event: AlertEventDB | None,
    status: str,
    cooldown_minutes: int | None,
) -> bool:
    """Per-channel dedup + cooldown check."""
    if last_event is None:
        return True
    if last_event.status != status:
        return True
    if cooldown_minutes is None:
        return False
    deadline = last_event.sent_at + timedelta(minutes=cooldown_minutes)
    return bool(datetime.now(UTC) >= deadline)


async def _send_to_channel(
    channel: AlertChannelDB,
    payload: AlertPayload,
    site_id: uuid.UUID,
    alert_type: str,
    status: str,
) -> None:
    sender = _SENDERS.get(channel.type)
    if not sender:
        logger.warning("Unknown channel type: %s", channel.type)
        return

    try:
        await sender.send(channel.config, payload)
        logger.info(
            "Alert sent via %s (%s) for site %s: %s=%s",
            channel.name,
            channel.type,
            payload.site_name,
            alert_type,
            status,
        )
    except Exception as e:
        logger.error(
            "Failed to send alert via %s (%s): %s",
            channel.name,
            channel.type,
            e,
            exc_info=True,
        )
        return  # Don't record the event if sending failed

    # Record event only on success (for deduplication + cooldown)
    async with AsyncSessionLocal() as db:
        event_repo = AlertEventRepository(db)
        await event_repo.record(site_id, channel.id, alert_type, status)


async def test_channel(channel: AlertChannelDB) -> tuple[bool, str]:
    """Send a test alert through a channel. Returns (success, message)."""
    sender = _SENDERS.get(channel.type)
    if not sender:
        return False, f"Unknown channel type: {channel.type}"
    try:
        message = await sender.test(channel.config)
        return True, message
    except Exception as e:
        return False, str(e)
