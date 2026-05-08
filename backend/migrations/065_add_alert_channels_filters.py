"""Migration 065: Add filters JSONB column to alert_channels."""

from sqlalchemy import text

from app.core.database import engine


async def upgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("""
            ALTER TABLE alert_channels
            ADD COLUMN IF NOT EXISTS filters JSONB NOT NULL DEFAULT '{}'::jsonb
        """))


async def downgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("""
            ALTER TABLE alert_channels
            DROP COLUMN IF EXISTS filters
        """))
