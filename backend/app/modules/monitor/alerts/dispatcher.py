"""Alert dispatcher — detects status changes and fans out to enabled channels."""

import logging
import uuid
from datetime import UTC, datetime

from app.core.database import AsyncSessionLocal

from ..db_models import SiteDB, SiteSnapshotDB
from .db_models import AlertChannelDB
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


async def dispatch_if_changed(
    site: SiteDB,
    snapshot: SiteSnapshotDB,
) -> None:
    """Check snapshot against last recorded alert; fire if status changed."""
    if not snapshot.status:
        return

    alert_type = _alert_type_for_snapshot(snapshot.snapshot_type, snapshot.status)
    if alert_type is None:
        return

    async with AsyncSessionLocal() as db:
        event_repo = AlertEventRepository(db)
        last_status = await event_repo.get_last_status(site.id, alert_type)

        # Only alert on status change (or first occurrence)
        if last_status == snapshot.status:
            return

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
        await _send_to_channel(channel, payload, site.id, alert_type, snapshot.status)


def _alert_type_for_snapshot(snapshot_type: str, status: str) -> str | None:
    """Map a snapshot type + status to an alert_type, or None if no alert needed."""
    if snapshot_type == "health" and status in _ALERT_STATUSES["health"]:
        return "health"
    if snapshot_type == "system" and status in _ALERT_STATUSES["reboot"]:
        return "reboot"
    if snapshot_type == "system" and status in _ALERT_STATUSES["updates"]:
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
        failed = [
            k
            for k, v in components.items()
            if isinstance(v, dict) and v.get("status") != "ok"
        ]
        if failed:
            return f"Affected components: {', '.join(failed)}"
    return None


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

    # Record event only on success (for deduplication)
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
