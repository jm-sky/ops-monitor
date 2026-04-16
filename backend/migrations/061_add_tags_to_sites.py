"""Migration 061: Add optional tags to sites."""

from sqlalchemy import text

from app.core.database import engine


async def upgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("""
            ALTER TABLE sites
            ADD COLUMN IF NOT EXISTS tags TEXT[]
        """))


async def downgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("""
            ALTER TABLE sites
            DROP COLUMN IF EXISTS tags
        """))
