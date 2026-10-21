"""Database access for package update events."""

import uuid
from datetime import datetime
from typing import Any

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from ..db_models import SiteDB
from .db_models import PackageUpdateEventDB


class PackageUpdateRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_latest_started_at(self, site_id: uuid.UUID) -> datetime | None:
        result = await self.db.execute(select(func.max(PackageUpdateEventDB.started_at)).where(PackageUpdateEventDB.site_id == site_id))
        return result.scalar_one_or_none()

    async def insert_ignore_duplicates(self, site_id: uuid.UUID, events: list[dict[str, Any]]) -> int:
        """Insert events, skipping any whose (site_id, started_at) already exists. Returns rows inserted."""
        if not events:
            return 0
        rows = [{"site_id": site_id, **event} for event in events]
        insert = sqlite_insert if self.db.get_bind().dialect.name == "sqlite" else pg_insert
        stmt = insert(PackageUpdateEventDB).values(rows).on_conflict_do_nothing(index_elements=["site_id", "started_at"])
        result = await self.db.execute(stmt)
        await self.db.commit()
        return max(result.rowcount or 0, 0)  # type: ignore[attr-defined]

    def _filtered(
        self,
        *,
        site_id: uuid.UUID | None,
        started_from: datetime | None,
        started_to: datetime | None,
        include_automatic: bool,
    ) -> list[Any]:
        conditions: list[Any] = []
        if site_id is not None:
            conditions.append(PackageUpdateEventDB.site_id == site_id)
        if started_from is not None:
            conditions.append(PackageUpdateEventDB.started_at >= started_from)
        if started_to is not None:
            conditions.append(PackageUpdateEventDB.started_at <= started_to)
        if not include_automatic:
            conditions.append(PackageUpdateEventDB.automatic.is_(False))
        return conditions

    async def query(
        self,
        *,
        site_id: uuid.UUID | None = None,
        started_from: datetime | None = None,
        started_to: datetime | None = None,
        include_automatic: bool = False,
        limit: int = 200,
        offset: int = 0,
    ) -> tuple[list[tuple[PackageUpdateEventDB, SiteDB]], int]:
        conditions = self._filtered(site_id=site_id, started_from=started_from, started_to=started_to, include_automatic=include_automatic)
        total = (await self.db.execute(select(func.count()).select_from(PackageUpdateEventDB).where(*conditions))).scalar_one()
        result = await self.db.execute(select(PackageUpdateEventDB, SiteDB).join(SiteDB, SiteDB.id == PackageUpdateEventDB.site_id).where(*conditions).order_by(PackageUpdateEventDB.started_at.desc(), PackageUpdateEventDB.id).limit(limit).offset(offset))
        return [(event, site) for event, site in result.all()], int(total)


def get_package_update_repository(db: AsyncSession = Depends(get_db)) -> PackageUpdateRepository:
    return PackageUpdateRepository(db)
