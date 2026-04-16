"""FastAPI router for monitor module — sites CRUD + snapshots."""

import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import AdminUser, CurrentUser

from .repositories import SnapshotRepository, SiteRepository
from .scheduler import activate_live_mode
from .schemas import (
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


# ---------------------------------------------------------------------------
# Sites
# ---------------------------------------------------------------------------


@router.get(
    "/sites",
    response_model=list[SiteResponse],
    summary="List sites",
)
async def list_sites(
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[SiteResponse]:
    repo = SiteRepository(db)
    sites = await repo.get_all()
    return [SiteResponse(**site.to_response()) for site in sites]


@router.get(
    "/site-statuses",
    response_model=list[SiteStatusResponse],
    summary="List sites with current status",
)
async def list_site_statuses(
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[SiteStatusResponse]:
    site_repo = SiteRepository(db)
    snap_repo = SnapshotRepository(db)

    sites = await site_repo.get_all()
    site_ids = [site.id for site in sites]
    snapshots_by_site = await snap_repo.get_latest_for_sites(site_ids)

    return [
        SiteStatusResponse(
            site=SiteResponse(**site.to_response()),
            healthSnapshot=(
                SiteSnapshotResponse(**health_snapshot.to_response())
                if (health_snapshot := snapshots_by_site.get(site.id, {}).get("health"))
                else None
            ),
            systemSnapshot=(
                SiteSnapshotResponse(**system_snapshot.to_response())
                if (system_snapshot := snapshots_by_site.get(site.id, {}).get("system"))
                else None
            ),
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
        "teams_webhook_url": data.teamsWebhookUrl,
        "server_label": data.serverLabel,
        "environment": data.environment,
        "verify_ssl": data.verifySSL,
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
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SiteStatusResponse:
    site_repo = SiteRepository(db)
    snap_repo = SnapshotRepository(db)

    site = await site_repo.get_by_id(site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Site not found"
        )

    health_snap = await snap_repo.get_latest(site_id, "health")
    system_snap = await snap_repo.get_latest(site_id, "system")

    return SiteStatusResponse(
        site=SiteResponse(**site.to_response()),
        healthSnapshot=(
            SiteSnapshotResponse(**health_snap.to_response()) if health_snap else None
        ),
        systemSnapshot=(
            SiteSnapshotResponse(**system_snap.to_response()) if system_snap else None
        ),
    )


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
    repo = SiteRepository(db)
    site = await repo.get_by_id(site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Site not found"
        )

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
        "teams_webhook_url": "teamsWebhookUrl",
        "server_label": "serverLabel",
        "environment": "environment",
        "verify_ssl": "verifySSL",
    }
    update_data = {
        db_field: getattr(data, schema_field)
        for db_field, schema_field in field_map.items()
        if schema_field in data.model_fields_set
    }
    site = await repo.update(site, update_data)
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Site not found"
        )
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
    if snapshot_type not in ("health", "system"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="snapshot_type must be 'health' or 'system'",
        )
    site_repo = SiteRepository(db)
    site = await site_repo.get_by_id(site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Site not found"
        )

    snap_repo = SnapshotRepository(db)
    snaps = await snap_repo.get_history(site_id, snapshot_type, limit=limit)
    return [SiteSnapshotResponse(**s.to_response()) for s in snaps]


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Site not found"
        )

    service = MonitorService()
    await service.poll_site_now(site)
    return PollResponse(message="Polling complete")


# ---------------------------------------------------------------------------
# Live mode heartbeat
# ---------------------------------------------------------------------------


@router.post(
    "/heartbeat",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Keep live mode active — call every ~30 s while dashboard is open",
)
async def heartbeat(_: CurrentUser) -> None:
    activate_live_mode()
