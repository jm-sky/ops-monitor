"""Migration 057: Create alert_channels table."""

from sqlalchemy import text

from app.core.database import engine


async def upgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS alert_channels (
                id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name        VARCHAR(255) NOT NULL UNIQUE,
                type        VARCHAR(50)  NOT NULL,
                enabled     BOOLEAN NOT NULL DEFAULT TRUE,
                config      JSONB NOT NULL DEFAULT '{}',
                created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_alert_channels_type
                ON alert_channels (type)
        """))
        # Track last alert sent per site to enable deduplication
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS alert_events (
                id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                site_id         UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
                channel_id      UUID NOT NULL REFERENCES alert_channels(id) ON DELETE CASCADE,
                alert_type      VARCHAR(50) NOT NULL,
                status          VARCHAR(50) NOT NULL,
                sent_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_alert_events_site_type
                ON alert_events (site_id, alert_type, sent_at DESC)
        """))


async def downgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS alert_events"))
        await conn.execute(text("DROP TABLE IF EXISTS alert_channels"))
