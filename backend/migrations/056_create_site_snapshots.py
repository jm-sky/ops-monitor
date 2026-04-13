"""Migration 056: Create site_snapshots table for monitor module."""

from sqlalchemy import text

from app.core.database import engine


async def upgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS site_snapshots (
                id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                site_id         UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
                snapshot_type   VARCHAR(20) NOT NULL,
                status          VARCHAR(50),
                raw_data        JSONB,
                error           TEXT,
                polled_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_site_snapshots_site_type_polled
                ON site_snapshots (site_id, snapshot_type, polled_at DESC)
        """))


async def downgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS site_snapshots"))
