"""FastAPI router for monitor module — sites CRUD + snapshots."""

import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.modules.auth.dependencies import AdminUser, CurrentUser

from .db_models import SiteDB, SiteSnapshotDB
from .health_schema import get_health_json_schema
from .repositories import SiteRepository, SnapshotRepository
from .scheduler import activate_live_mode
from .schemas import (
    MonitorConfigResponse,
    PaginatedSiteSnapshotResponse,
    PollResponse,
    SiteCreate,
    SiteResponse,
    SiteSnapshotResponse,
    SiteStatusResponse,
    SiteUpdate,
)
from .service import MonitorService

router = APIRouter()
logger = logging.getLogger(__name__)


def _snapshot_for_site(
    site: SiteDB,
    snapshot: SiteSnapshotDB | None,
    snapshot_type: str,
) -> SiteSnapshotDB | None:
    """Return snapshot only when the site has the corresponding URL configured."""
    if snapshot is None:
        return None
    if snapshot_type == "health" and site.health_url:
        return snapshot
    if snapshot_type == "system" and site.system_url:
        return snapshot
    if snapshot_type == "ssl" and site.ssl_check_url:
        return snapshot
    return None


def _site_response(site: SiteDB, *, redact_secrets: bool) -> SiteResponse:
    """Build a SiteResponse, stripping polling-secret fields for non-admins.

    `token` (bearer credential used to poll the site's /health + /system) and
    `teamsWebhookUrl` let anyone holding them hit those endpoints directly or
    post into the org's Teams channel — they must not be visible to a
    non-admin just because they're logged in. See SEC-1 in
    docs/reviews/2026-07-20-security-backend.md.
    """
    response = SiteResponse(**site.to_response())
    if redact_secrets:
        response = response.model_copy(update={"token": None, "teamsWebhookUrl": None})
    return response


def _site_status_response(
    site: SiteDB,
    health_snapshot: SiteSnapshotDB | None,
    system_snapshot: SiteSnapshotDB | None,
    ssl_snapshot: SiteSnapshotDB | None = None,
    *,
    redact_secrets: bool = False,
) -> SiteStatusResponse:
    health = _snapshot_for_site(site, health_snapshot, "health")
    system = _snapshot_for_site(site, system_snapshot, "system")
    ssl_snap = _snapshot_for_site(site, ssl_snapshot, "ssl")
    return SiteStatusResponse(
        site=_site_response(site, redact_secrets=redact_secrets),
        healthSnapshot=(SiteSnapshotResponse(**health.to_response()) if health else None),
        systemSnapshot=(SiteSnapshotResponse(**system.to_response()) if system else None),
        sslSnapshot=(SiteSnapshotResponse(**ssl_snap.to_response()) if ssl_snap else None),
    )


# ---------------------------------------------------------------------------
# Runtime config
# ---------------------------------------------------------------------------


@router.get(
    "/config",
    response_model=MonitorConfigResponse,
    summary="Monitoring runtime configuration for frontend and scheduler",
)
async def get_monitor_config(_: CurrentUser) -> MonitorConfigResponse:
    return MonitorConfigResponse(
        checkIntervalSeconds=settings.monitor.check_interval_seconds,
        livePollIntervalSeconds=settings.monitor.live_poll_interval_seconds,
        liveModeTtlSeconds=settings.monitor.live_mode_ttl_seconds,
        uiBackgroundRefetchSeconds=settings.monitor.ui_background_refetch_seconds,
        uiActiveRefetchSeconds=settings.monitor.ui_active_refetch_seconds,
        heartbeatIntervalSeconds=settings.monitor.heartbeat_interval_seconds,
    )


# ---------------------------------------------------------------------------
# Health schema
# ---------------------------------------------------------------------------


@router.get(
    "/health-schema.json",
    summary="JSON Schema for the /health endpoint contract",
    include_in_schema=True,
)
async def health_schema() -> dict:
    return get_health_json_schema()


# ---------------------------------------------------------------------------
# Sites
# ---------------------------------------------------------------------------


@router.get(
    "/sites",
    response_model=list[SiteResponse],
    summary="List sites",
)
async def list_sites(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[SiteResponse]:
    repo = SiteRepository(db)
    sites = await repo.get_all()
    is_admin = current_user.isAdmin or current_user.isOwner
    return [_site_response(site, redact_secrets=not is_admin) for site in sites]


@router.get(
    "/site-statuses",
    response_model=list[SiteStatusResponse],
    summary="List sites with current status",
)
async def list_site_statuses(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[SiteStatusResponse]:
    site_repo = SiteRepository(db)
    snap_repo = SnapshotRepository(db)

    sites = await site_repo.get_all()
    site_ids = [site.id for site in sites]
    snapshots_by_site = await snap_repo.get_latest_for_sites(site_ids)
    is_admin = current_user.isAdmin or current_user.isOwner

    return [
        _site_status_response(
            site,
            snapshots_by_site.get(site.id, {}).get("health"),
            snapshots_by_site.get(site.id, {}).get("system"),
            snapshots_by_site.get(site.id, {}).get("ssl"),
            redact_secrets=not is_admin,
        )
        for site in sites
    ]


@router.post(
    "/sites",
    response_model=SiteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create site",
)
async def create_site(
    data: SiteCreate,
    _: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SiteResponse:
    repo = SiteRepository(db)
    site_data = {
        "name": data.name,
        "description": data.description,
        "health_url": data.healthUrl,
        "system_url": data.systemUrl,
        "token": data.token,
        "tags": data.tags,
        "enabled": data.enabled,
        "polling_health": data.pollingHealth,
        "polling_system": data.pollingSystem,
        "polling_updates": data.pollingUpdates,
        "polling_reboot": data.pollingReboot,
        "ssl_check_url": data.sslCheckUrl,
        "polling_ssl": data.pollingSsl,
        "teams_webhook_url": data.teamsWebhookUrl,
        "server_label": data.serverLabel,
        "environment": data.environment,
        "verify_ssl": data.verifySSL,
        "ip": data.ip,
        "expected_meta": data.expectedMeta,
    }
    site = await repo.create(site_data)
    return SiteResponse(**site.to_response())


@router.get(
    "/sites/{site_id}",
    response_model=SiteStatusResponse,
    summary="Get site with current status",
)
async def get_site(
    site_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SiteStatusResponse:
    site_repo = SiteRepository(db)
    snap_repo = SnapshotRepository(db)

    site = await site_repo.get_by_id(site_id)
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    health_snap = await snap_repo.get_latest(site_id, "health")
    system_snap = await snap_repo.get_latest(site_id, "system")
    ssl_snap = await snap_repo.get_latest(site_id, "ssl")
    is_admin = current_user.isAdmin or current_user.isOwner

    return _site_status_response(site, health_snap, system_snap, ssl_snap, redact_secrets=not is_admin)


@router.put(
    "/sites/{site_id}",
    response_model=SiteResponse,
    summary="Update site",
)
async def update_site(
    site_id: uuid.UUID,
    data: SiteUpdate,
    _: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SiteResponse:
    site_repo = SiteRepository(db)
    snap_repo = SnapshotRepository(db)
    site = await site_repo.get_by_id(site_id)
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    field_map = {
        "name": "name",
        "description": "description",
        "health_url": "healthUrl",
        "system_url": "systemUrl",
        "token": "token",
        "tags": "tags",
        "enabled": "enabled",
        "polling_health": "pollingHealth",
        "polling_system": "pollingSystem",
        "polling_updates": "pollingUpdates",
        "polling_reboot": "pollingReboot",
        "ssl_check_url": "sslCheckUrl",
        "polling_ssl": "pollingSsl",
        "teams_webhook_url": "teamsWebhookUrl",
        "server_label": "serverLabel",
        "environment": "environment",
        "verify_ssl": "verifySSL",
        "ip": "ip",
        "expected_meta": "expectedMeta",
    }
    update_data = {db_field: getattr(data, schema_field) for db_field, schema_field in field_map.items() if schema_field in data.model_fields_set}
    if "healthUrl" in data.model_fields_set and not data.healthUrl:
        await snap_repo.delete_all_for_type(site_id, "health")
    if "systemUrl" in data.model_fields_set and not data.systemUrl:
        await snap_repo.delete_all_for_type(site_id, "system")
    if "sslCheckUrl" in data.model_fields_set and not data.sslCheckUrl:
        await snap_repo.delete_all_for_type(site_id, "ssl")
    site = await site_repo.update(site, update_data)
    return SiteResponse(**site.to_response())


@router.delete(
    "/sites/{site_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete site",
)
async def delete_site(
    site_id: uuid.UUID,
    _: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    repo = SiteRepository(db)
    site = await repo.get_by_id(site_id)
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
    await repo.delete(site)


# ---------------------------------------------------------------------------
# Snapshots
# ---------------------------------------------------------------------------


@router.get(
    "/sites/{site_id}/snapshots/{snapshot_type}",
    response_model=list[SiteSnapshotResponse],
    summary="Get snapshot history for a site",
)
async def get_snapshots(
    site_id: uuid.UUID,
    snapshot_type: str,
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(100, ge=1, le=500),
) -> list[SiteSnapshotResponse]:
    if snapshot_type not in ("health", "system", "ssl"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="snapshot_type must be 'health', 'system' or 'ssl'",
        )
    site_repo = SiteRepository(db)
    site = await site_repo.get_by_id(site_id)
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    snap_repo = SnapshotRepository(db)
    snaps = await snap_repo.get_history(site_id, snapshot_type, limit=limit)
    return [SiteSnapshotResponse(**s.to_response()) for s in snaps]


@router.get(
    "/sites/{site_id}/snapshots/{snapshot_type}/page",
    response_model=PaginatedSiteSnapshotResponse,
    summary="Get paginated snapshot history for a site",
)
async def get_snapshots_page(
    site_id: uuid.UUID,
    snapshot_type: str,
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(10, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> PaginatedSiteSnapshotResponse:
    if snapshot_type not in ("health", "system", "ssl"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="snapshot_type must be 'health', 'system' or 'ssl'",
        )
    site_repo = SiteRepository(db)
    site = await site_repo.get_by_id(site_id)
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    snap_repo = SnapshotRepository(db)
    total = await snap_repo.count_history(site_id, snapshot_type)
    snaps = await snap_repo.get_history_page(site_id, snapshot_type, limit=limit, offset=offset)
    return PaginatedSiteSnapshotResponse(
        items=[SiteSnapshotResponse(**s.to_response()) for s in snaps],
        total=total,
    )


# ---------------------------------------------------------------------------
# On-demand poll
# ---------------------------------------------------------------------------


@router.post(
    "/sites/{site_id}/poll",
    response_model=PollResponse,
    summary="Trigger immediate poll for a site",
)
async def poll_now(
    site_id: uuid.UUID,
    _: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PollResponse:
    repo = SiteRepository(db)
    site = await repo.get_by_id(site_id)
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    service = MonitorService()
    await service.poll_site_now(site)
    return PollResponse(message="Polling complete")


# ---------------------------------------------------------------------------
# Live mode heartbeat
# ---------------------------------------------------------------------------


@router.post(
    "/heartbeat",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Keep live mode active — call at configured heartbeat interval while dashboard is open",
)
async def heartbeat(_: CurrentUser) -> None:
    activate_live_mode()
