"""FastAPI router for alert channels CRUD + test."""

import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import AdminUser, CurrentUser

from .dispatcher import test_channel
from .repositories import AlertChannelRepository, AlertEventRepository
from .schemas import (
    AlertChannelCreate,
    AlertChannelResponse,
    AlertChannelUpdate,
    AlertEventResponse,
    TestAlertResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/alert-channels",
    response_model=list[AlertChannelResponse],
    summary="List alert channels",
)
async def list_channels(
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[AlertChannelResponse]:
    repo = AlertChannelRepository(db)
    channels = await repo.get_all()
    return [AlertChannelResponse(**c.to_response()) for c in channels]


@router.post(
    "/alert-channels",
    response_model=AlertChannelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create alert channel",
)
async def create_channel(
    data: AlertChannelCreate,
    _: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AlertChannelResponse:
    repo = AlertChannelRepository(db)
    channel_data = {
        "name": data.name,
        "type": data.type,
        "enabled": data.enabled,
        "config": data.config,
    }
    channel = await repo.create(channel_data)
    return AlertChannelResponse(**channel.to_response())


@router.get(
    "/alert-channels/{channel_id}",
    response_model=AlertChannelResponse,
    summary="Get alert channel",
)
async def get_channel(
    channel_id: uuid.UUID,
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AlertChannelResponse:
    repo = AlertChannelRepository(db)
    channel = await repo.get_by_id(channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found"
        )
    return AlertChannelResponse(**channel.to_response())


@router.put(
    "/alert-channels/{channel_id}",
    response_model=AlertChannelResponse,
    summary="Update alert channel",
)
async def update_channel(
    channel_id: uuid.UUID,
    data: AlertChannelUpdate,
    _: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AlertChannelResponse:
    repo = AlertChannelRepository(db)
    channel = await repo.get_by_id(channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found"
        )

    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    channel = await repo.update(channel, update_data)
    return AlertChannelResponse(**channel.to_response())


@router.delete(
    "/alert-channels/{channel_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete alert channel",
)
async def delete_channel(
    channel_id: uuid.UUID,
    _: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    repo = AlertChannelRepository(db)
    channel = await repo.get_by_id(channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found"
        )
    await repo.delete(channel)


@router.post(
    "/alert-channels/{channel_id}/test",
    response_model=TestAlertResponse,
    summary="Send test alert through channel",
)
async def test_channel_endpoint(
    channel_id: uuid.UUID,
    _: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TestAlertResponse:
    repo = AlertChannelRepository(db)
    channel = await repo.get_by_id(channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found"
        )

    success, message = await test_channel(channel)
    return TestAlertResponse(success=success, message=message)


# ---------------------------------------------------------------------------
# Alert event log
# ---------------------------------------------------------------------------


@router.get(
    "/alert-events",
    response_model=list[AlertEventResponse],
    summary="List recent alert events",
)
async def list_alert_events(
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(100, ge=1, le=500),
    site_id: uuid.UUID | None = Query(None),
) -> list[AlertEventResponse]:
    repo = AlertEventRepository(db)
    rows = await repo.get_recent(limit=limit, site_id=site_id)
    return [
        AlertEventResponse(
            id=str(event.id),
            siteId=str(event.site_id),
            siteName=site_name,
            channelId=str(event.channel_id),
            channelName=channel_name,
            alertType=event.alert_type,
            status=event.status,
            sentAt=event.sent_at,
        )
        for event, site_name, channel_name in rows
    ]
