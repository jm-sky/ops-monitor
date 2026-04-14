"""Migration 058: Add optional server_label to sites."""

from sqlalchemy import text

from app.core.database import engine


async def upgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("""
            ALTER TABLE sites
            ADD COLUMN IF NOT EXISTS server_label VARCHAR(255)
        """))


async def downgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("""
            ALTER TABLE sites
            DROP COLUMN IF EXISTS server_label
        """))
