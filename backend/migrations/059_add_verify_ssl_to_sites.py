"""Migration 059: Add verify_ssl flag to sites (default True)."""

from sqlalchemy import text

from app.core.database import engine


async def upgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("""
            ALTER TABLE sites
            ADD COLUMN IF NOT EXISTS verify_ssl BOOLEAN NOT NULL DEFAULT TRUE
        """))


async def downgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("""
            ALTER TABLE sites
            DROP COLUMN IF EXISTS verify_ssl
        """))
