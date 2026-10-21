"""Migration 070: Create api_keys table (hashed read-only service tokens)."""

from sqlalchemy import text

from app.core.database import engine


async def upgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name            VARCHAR(255) NOT NULL,
                key_prefix      VARCHAR(16) NOT NULL,
                key_hash        VARCHAR(64) NOT NULL UNIQUE,
                scopes          JSONB NOT NULL DEFAULT '[]'::jsonb,
                created_by      VARCHAR(64),
                created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                expires_at      TIMESTAMPTZ,
                last_used_at    TIMESTAMPTZ,
                revoked_at      TIMESTAMPTZ
            )
        """))


async def downgrade() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS api_keys"))
