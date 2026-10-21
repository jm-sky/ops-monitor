"""FastAPI dependency authenticating requests by scoped API key (Bearer)."""

from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .db_models import ApiKeyDB
from .repositories import ApiKeyRepository, get_api_key_repository
from .service import ApiKeyService

_bearer = HTTPBearer(auto_error=False)


def require_api_key_scope(scope: str) -> Callable[..., Awaitable[ApiKeyDB]]:
    """Build a dependency that accepts only an active API key granting *scope*.

    Missing, unknown, revoked, expired and wrong-scope keys all yield the same 401 so the
    response does not reveal which keys exist.
    """

    async def dependency(
        credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
        repository: Annotated[ApiKeyRepository, Depends(get_api_key_repository)],
    ) -> ApiKeyDB:
        key = await ApiKeyService(repository).authenticate(credentials.credentials, scope) if credentials else None
        if key is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return key

    return dependency
