"""Migration 060: Add optional environment to sites."""

from sqlalchemy import text

from app.core.database import engine


async def upgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("""
            ALTER TABLE sites
            ADD COLUMN IF NOT EXISTS environment VARCHAR(100)
        """))


async def downgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("""
            ALTER TABLE sites
            DROP COLUMN IF EXISTS environment
        """))
