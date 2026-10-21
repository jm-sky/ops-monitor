"""API key generation, hashing and verification.

Keys are ``opsm_`` + 32 random bytes (urlsafe base64). They carry enough entropy that a
plain SHA-256 digest is sufficient at rest (no slow KDF needed); only the digest and a short
display prefix are stored, so a database leak does not expose usable keys.
"""

import hashlib
import secrets
from datetime import UTC, datetime

from .db_models import ALLOWED_SCOPES, ApiKeyDB
from .repositories import ApiKeyRepository

KEY_PREFIX = "opsm_"
_DISPLAY_PREFIX_LENGTH = len(KEY_PREFIX) + 4


class InvalidScopeError(ValueError):
    pass


def hash_api_key(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def generate_api_key() -> str:
    return f"{KEY_PREFIX}{secrets.token_urlsafe(32)}"


def validate_scopes(scopes: list[str]) -> list[str]:
    unknown = sorted(set(scopes) - set(ALLOWED_SCOPES))
    if unknown:
        raise InvalidScopeError(f"Unknown scope(s): {', '.join(unknown)}. Allowed: {', '.join(ALLOWED_SCOPES)}")
    return sorted(set(scopes))


def _is_expired(key: ApiKeyDB, now: datetime) -> bool:
    if key.expires_at is None:
        return False
    expires_at = key.expires_at if key.expires_at.tzinfo else key.expires_at.replace(tzinfo=UTC)
    return expires_at <= now


class ApiKeyService:
    def __init__(self, repository: ApiKeyRepository) -> None:
        self.repository = repository

    async def create(self, name: str, scopes: list[str], created_by: str | None, expires_at: datetime | None = None) -> tuple[ApiKeyDB, str]:
        """Create a key; returns the stored row and the plaintext key (shown once)."""
        validated = validate_scopes(scopes)
        plaintext = generate_api_key()
        row = ApiKeyDB(
            name=name,
            key_prefix=plaintext[:_DISPLAY_PREFIX_LENGTH],
            key_hash=hash_api_key(plaintext),
            scopes=validated,
            created_by=created_by,
            expires_at=expires_at,
        )
        return await self.repository.create(row), plaintext

    async def authenticate(self, plaintext: str, required_scope: str) -> ApiKeyDB | None:
        """Return the key when it exists, is active, unexpired and grants *required_scope*."""
        if not plaintext.startswith(KEY_PREFIX):
            return None
        key = await self.repository.get_by_hash(hash_api_key(plaintext))
        if key is None or key.revoked_at is not None or _is_expired(key, datetime.now(UTC)):
            return None
        if required_scope not in (key.scopes or []):
            return None
        await self.repository.touch_last_used(key)
        return key
