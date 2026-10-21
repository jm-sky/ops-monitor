"""Database access for API keys."""

import uuid
from datetime import UTC, datetime, timedelta

from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from .db_models import ApiKeyDB

# Throttle last_used_at writes so a polling client doesn't write on every request.
_LAST_USED_RESOLUTION = timedelta(minutes=1)


class ApiKeyRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, key: ApiKeyDB) -> ApiKeyDB:
        self.db.add(key)
        await self.db.commit()
        await self.db.refresh(key)
        return key

    async def list_all(self) -> list[ApiKeyDB]:
        result = await self.db.execute(select(ApiKeyDB).order_by(ApiKeyDB.created_at.desc()))
        return list(result.scalars().all())

    async def get_by_id(self, key_id: uuid.UUID) -> ApiKeyDB | None:
        result = await self.db.execute(select(ApiKeyDB).where(ApiKeyDB.id == key_id))
        return result.scalar_one_or_none()

    async def get_by_hash(self, key_hash: str) -> ApiKeyDB | None:
        result = await self.db.execute(select(ApiKeyDB).where(ApiKeyDB.key_hash == key_hash))
        return result.scalar_one_or_none()

    async def revoke(self, key: ApiKeyDB) -> ApiKeyDB:
        key.revoked_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(key)
        return key

    async def touch_last_used(self, key: ApiKeyDB) -> None:
        now = datetime.now(UTC)
        last = key.last_used_at
        if last is not None:
            if last.tzinfo is None:
                last = last.replace(tzinfo=UTC)
            if now - last < _LAST_USED_RESOLUTION:
                return
        await self.db.execute(update(ApiKeyDB).where(ApiKeyDB.id == key.id).values(last_used_at=now))
        await self.db.commit()


def get_api_key_repository(db: AsyncSession = Depends(get_db)) -> ApiKeyRepository:
    return ApiKeyRepository(db)
