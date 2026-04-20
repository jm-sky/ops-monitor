"""Migration 064: Add meta_mismatches JSONB to site_snapshots."""

from sqlalchemy import text

from app.core.database import engine


async def upgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("""
            ALTER TABLE site_snapshots
            ADD COLUMN IF NOT EXISTS meta_mismatches JSONB
        """))


async def downgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("""
            ALTER TABLE site_snapshots
            DROP COLUMN IF EXISTS meta_mismatches
        """))
