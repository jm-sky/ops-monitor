"""Repositories for alert channels and alert events."""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .db_models import AlertChannelDB, AlertEventDB


class AlertChannelRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all(self) -> list[AlertChannelDB]:
        result = await self.db.execute(
            select(AlertChannelDB).order_by(AlertChannelDB.name)
        )
        return list(result.scalars().all())

    async def get_enabled(self) -> list[AlertChannelDB]:
        result = await self.db.execute(
            select(AlertChannelDB)
            .where(AlertChannelDB.enabled.is_(True))
            .order_by(AlertChannelDB.name)
        )
        return list(result.scalars().all())

    async def get_by_id(self, channel_id: uuid.UUID) -> AlertChannelDB | None:
        result = await self.db.execute(
            select(AlertChannelDB).where(AlertChannelDB.id == channel_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: dict[str, Any]) -> AlertChannelDB:
        channel = AlertChannelDB(**data)
        self.db.add(channel)
        await self.db.commit()
        await self.db.refresh(channel)
        return channel

    async def update(
        self, channel: AlertChannelDB, data: dict[str, Any]
    ) -> AlertChannelDB:
        for key, value in data.items():
            setattr(channel, key, value)
        channel.updated_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(channel)
        return channel

    async def delete(self, channel: AlertChannelDB) -> None:
        await self.db.delete(channel)
        await self.db.commit()


class AlertEventRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_last_status(self, site_id: uuid.UUID, alert_type: str) -> str | None:
        """Return the status of the most recently sent alert for this site+type."""
        result = await self.db.execute(
            select(AlertEventDB.status)
            .where(
                AlertEventDB.site_id == site_id,
                AlertEventDB.alert_type == alert_type,
            )
            .order_by(AlertEventDB.sent_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def record(
        self,
        site_id: uuid.UUID,
        channel_id: uuid.UUID,
        alert_type: str,
        status: str,
    ) -> None:
        event = AlertEventDB(
            site_id=site_id,
            channel_id=channel_id,
            alert_type=alert_type,
            status=status,
            sent_at=datetime.now(UTC),
        )
        self.db.add(event)
        await self.db.commit()
