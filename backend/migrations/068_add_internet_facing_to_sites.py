"""Migration 068: Add internet_facing flag to sites."""

from sqlalchemy import text

from app.core.database import engine


async def upgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("""
            ALTER TABLE sites
            ADD COLUMN IF NOT EXISTS internet_facing BOOLEAN NOT NULL DEFAULT FALSE
        """))


async def downgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("""
            ALTER TABLE sites
            DROP COLUMN IF EXISTS internet_facing
        """))
