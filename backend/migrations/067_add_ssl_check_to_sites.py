"""Migration 067: Add SSL certificate check fields to sites."""

from sqlalchemy import text

from app.core.database import engine


async def upgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("""
                ALTER TABLE sites
                ADD COLUMN IF NOT EXISTS ssl_check_url VARCHAR(500) NULL
                """))
        await conn.execute(text("""
                ALTER TABLE sites
                ADD COLUMN IF NOT EXISTS polling_ssl INTEGER NOT NULL DEFAULT 43200
                """))


async def downgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("""
                ALTER TABLE sites
                DROP COLUMN IF EXISTS polling_ssl
                """))
        await conn.execute(text("""
                ALTER TABLE sites
                DROP COLUMN IF EXISTS ssl_check_url
                """))
