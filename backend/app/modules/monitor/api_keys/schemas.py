"""Pydantic schemas for API key management."""

from datetime import datetime

from pydantic import BaseModel, Field


class ApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    scopes: list[str] = Field(..., min_length=1)
    expiresAt: datetime | None = None


class ApiKeyResponse(BaseModel):
    id: str
    name: str
    keyPrefix: str
    scopes: list[str]
    createdBy: str | None = None
    createdAt: datetime
    expiresAt: datetime | None = None
    lastUsedAt: datetime | None = None
    revokedAt: datetime | None = None


class ApiKeyCreatedResponse(ApiKeyResponse):
    """Returned once on creation — ``key`` is never retrievable again."""

    key: str
