"""Admin endpoints for managing service API keys."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.auth.dependencies import AdminUser

from .db_models import ApiKeyDB
from .repositories import ApiKeyRepository, get_api_key_repository
from .schemas import ApiKeyCreate, ApiKeyCreatedResponse, ApiKeyResponse
from .service import ApiKeyService, InvalidScopeError

router = APIRouter()


def _to_response(key: ApiKeyDB) -> ApiKeyResponse:
    return ApiKeyResponse(
        id=str(key.id),
        name=key.name,
        keyPrefix=key.key_prefix,
        scopes=list(key.scopes or []),
        createdBy=key.created_by,
        createdAt=key.created_at,
        expiresAt=key.expires_at,
        lastUsedAt=key.last_used_at,
        revokedAt=key.revoked_at,
    )


@router.get("/api-keys", response_model=list[ApiKeyResponse], summary="List API keys (admin)")
async def list_api_keys(
    _: AdminUser,
    repository: Annotated[ApiKeyRepository, Depends(get_api_key_repository)],
) -> list[ApiKeyResponse]:
    return [_to_response(key) for key in await repository.list_all()]


@router.post(
    "/api-keys",
    response_model=ApiKeyCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create API key (admin) — the plaintext key is returned only once",
)
async def create_api_key(
    data: ApiKeyCreate,
    admin: AdminUser,
    repository: Annotated[ApiKeyRepository, Depends(get_api_key_repository)],
) -> ApiKeyCreatedResponse:
    try:
        key, plaintext = await ApiKeyService(repository).create(data.name, data.scopes, created_by=str(admin.id), expires_at=data.expiresAt)
    except InvalidScopeError as e:
        raise HTTPException(status_code=422, detail=str(e)) from None
    return ApiKeyCreatedResponse(**_to_response(key).model_dump(), key=plaintext)


@router.delete("/api-keys/{key_id}", response_model=ApiKeyResponse, summary="Revoke API key (admin)")
async def revoke_api_key(
    key_id: uuid.UUID,
    _: AdminUser,
    repository: Annotated[ApiKeyRepository, Depends(get_api_key_repository)],
) -> ApiKeyResponse:
    key = await repository.get_by_id(key_id)
    if key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
    if key.revoked_at is None:
        key = await repository.revoke(key)
    return _to_response(key)
