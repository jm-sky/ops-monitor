"""Migration 055: Create sites table for monitor module."""

from app.core.database import get_engine


async def upgrade() -> None:
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.execute(__import__("sqlalchemy", fromlist=["text"]).text("""
                CREATE TABLE IF NOT EXISTS sites (
                    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name            VARCHAR(255) NOT NULL UNIQUE,
                    description     TEXT,
                    health_url      VARCHAR(500),
                    system_url      VARCHAR(500),
                    token           VARCHAR(500),
                    enabled         BOOLEAN NOT NULL DEFAULT TRUE,
                    polling_health  INTEGER NOT NULL DEFAULT 300,
                    polling_system  INTEGER NOT NULL DEFAULT 300,
                    polling_updates INTEGER NOT NULL DEFAULT 43200,
                    polling_reboot  INTEGER NOT NULL DEFAULT 1800,
                    teams_webhook_url VARCHAR(500),
                    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """))


async def downgrade() -> None:
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.execute(__import__("sqlalchemy", fromlist=["text"]).text("DROP TABLE IF EXISTS sites"))
