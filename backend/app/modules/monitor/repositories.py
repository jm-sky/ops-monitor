"""Database repositories for monitor module."""

import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import Depends
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from .db_models import SiteDB, SiteSnapshotDB


class SiteRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all(self) -> list[SiteDB]:
        result = await self.db.execute(select(SiteDB).order_by(SiteDB.name))
        return list(result.scalars().all())

    async def get_enabled(self) -> list[SiteDB]:
        result = await self.db.execute(select(SiteDB).where(SiteDB.enabled.is_(True)).order_by(SiteDB.name))
        return list(result.scalars().all())

    async def get_by_id(self, site_id: uuid.UUID) -> SiteDB | None:
        result = await self.db.execute(select(SiteDB).where(SiteDB.id == site_id))
        return result.scalar_one_or_none()

    async def create(self, data: dict[str, Any]) -> SiteDB:
        site = SiteDB(**data)
        self.db.add(site)
        await self.db.commit()
        await self.db.refresh(site)
        return site

    async def update(self, site: SiteDB, data: dict[str, Any]) -> SiteDB:
        for key, value in data.items():
            setattr(site, key, value)
        site.updated_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(site)
        return site

    async def delete(self, site: SiteDB) -> None:
        await self.db.delete(site)
        await self.db.commit()


class SnapshotRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        site_id: uuid.UUID,
        snapshot_type: str,
        raw_data: dict | None,
        error: str | None,
        status: str | None,
        meta_mismatches: list[str] | None = None,
    ) -> SiteSnapshotDB:
        snap = SiteSnapshotDB(
            site_id=site_id,
            snapshot_type=snapshot_type,
            raw_data=raw_data,
            meta_mismatches=meta_mismatches or None,
            error=error,
            status=status,
            polled_at=datetime.now(UTC),
        )
        self.db.add(snap)
        await self.db.commit()
        await self.db.refresh(snap)
        return snap

    async def get_latest(self, site_id: uuid.UUID, snapshot_type: str) -> SiteSnapshotDB | None:
        result = await self.db.execute(
            select(SiteSnapshotDB)
            .where(
                SiteSnapshotDB.site_id == site_id,
                SiteSnapshotDB.snapshot_type == snapshot_type,
            )
            .order_by(SiteSnapshotDB.polled_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_latest_for_sites(self, site_ids: list[uuid.UUID]) -> dict[uuid.UUID, dict[str, SiteSnapshotDB]]:
        """Return latest snapshots grouped by site id and snapshot type."""
        if not site_ids:
            return {}

        ranked = (
            select(
                SiteSnapshotDB.id.label("id"),
                SiteSnapshotDB.site_id.label("site_id"),
                SiteSnapshotDB.snapshot_type.label("snapshot_type"),
                func.row_number()
                .over(
                    partition_by=(
                        SiteSnapshotDB.site_id,
                        SiteSnapshotDB.snapshot_type,
                    ),
                    order_by=SiteSnapshotDB.polled_at.desc(),
                )
                .label("rn"),
            )
            .where(SiteSnapshotDB.site_id.in_(site_ids))
            .subquery()
        )

        result = await self.db.execute(select(SiteSnapshotDB).join(ranked, ranked.c.id == SiteSnapshotDB.id).where(ranked.c.rn == 1))

        snapshots_by_site: dict[uuid.UUID, dict[str, SiteSnapshotDB]] = {}
        for snapshot in result.scalars().all():
            snapshots_by_site.setdefault(snapshot.site_id, {})[snapshot.snapshot_type] = snapshot
        return snapshots_by_site

    async def get_history(self, site_id: uuid.UUID, snapshot_type: str, limit: int = 100) -> list[SiteSnapshotDB]:
        result = await self.db.execute(
            select(SiteSnapshotDB)
            .where(
                SiteSnapshotDB.site_id == site_id,
                SiteSnapshotDB.snapshot_type == snapshot_type,
            )
            .order_by(SiteSnapshotDB.polled_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_history(self, site_id: uuid.UUID, snapshot_type: str) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(SiteSnapshotDB)
            .where(
                SiteSnapshotDB.site_id == site_id,
                SiteSnapshotDB.snapshot_type == snapshot_type,
            )
        )
        return int(result.scalar_one())

    async def get_history_page(
        self,
        site_id: uuid.UUID,
        snapshot_type: str,
        limit: int,
        offset: int,
    ) -> list[SiteSnapshotDB]:
        result = await self.db.execute(
            select(SiteSnapshotDB)
            .where(
                SiteSnapshotDB.site_id == site_id,
                SiteSnapshotDB.snapshot_type == snapshot_type,
            )
            .order_by(SiteSnapshotDB.polled_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def delete_all_for_type(self, site_id: uuid.UUID, snapshot_type: str) -> None:
        """Delete all snapshots for a site and snapshot type."""
        await self.db.execute(
            delete(SiteSnapshotDB).where(
                SiteSnapshotDB.site_id == site_id,
                SiteSnapshotDB.snapshot_type == snapshot_type,
            )
        )
        await self.db.commit()

    async def cleanup_old(self, site_id: uuid.UUID, snapshot_type: str, keep: int = 1000) -> None:
        """Delete all but the most recent `keep` snapshots for a site+type."""
        subq = (
            select(SiteSnapshotDB.id)
            .where(
                SiteSnapshotDB.site_id == site_id,
                SiteSnapshotDB.snapshot_type == snapshot_type,
            )
            .order_by(SiteSnapshotDB.polled_at.desc())
            .limit(keep)
            .subquery()
        )
        await self.db.execute(
            delete(SiteSnapshotDB)
            .where(
                SiteSnapshotDB.site_id == site_id,
                SiteSnapshotDB.snapshot_type == snapshot_type,
            )
            .where(SiteSnapshotDB.id.not_in(select(subq.c.id)))
        )
        await self.db.commit()


def get_site_repository(db: AsyncSession = Depends(get_db)) -> SiteRepository:
    return SiteRepository(db)


def get_snapshot_repository(db: AsyncSession = Depends(get_db)) -> SnapshotRepository:
    return SnapshotRepository(db)
