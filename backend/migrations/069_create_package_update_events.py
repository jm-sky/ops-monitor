"""Migration 069: Create package_update_events table (apt history pulled from agents)."""

from sqlalchemy import text

from app.core.database import engine


async def upgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS package_update_events (
                id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                site_id         UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
                started_at      TIMESTAMPTZ NOT NULL,
                finished_at     TIMESTAMPTZ,
                commandline     TEXT,
                requested_by    VARCHAR(255),
                automatic       BOOLEAN NOT NULL DEFAULT FALSE,
                packages        JSONB NOT NULL DEFAULT '{}'::jsonb,
                created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                CONSTRAINT uq_package_update_events_site_started UNIQUE (site_id, started_at)
            )
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_package_update_events_started_at
                ON package_update_events (started_at DESC)
        """))


async def downgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS package_update_events"))
