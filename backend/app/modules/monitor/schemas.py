"""Pydantic schemas for monitor module API."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

MetaValue = str | int | float | bool


class SiteCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    healthUrl: str | None = None
    systemUrl: str | None = None
    token: str | None = None
    tags: list[str] | None = None
    enabled: bool = True
    pollingHealth: int = Field(300, ge=30)
    pollingSystem: int = Field(300, ge=30)
    pollingUpdates: int = Field(43200, ge=300)
    pollingReboot: int = Field(1800, ge=60)
    sslCheckUrl: str | None = None
    pollingSsl: int = Field(43200, ge=300)
    teamsWebhookUrl: str | None = None
    serverLabel: str | None = Field(None, max_length=255)
    environment: str | None = Field(None, max_length=100)
    verifySSL: bool = True
    ip: str | None = Field(None, max_length=45)
    expectedMeta: dict[str, MetaValue] | None = None


class SiteUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    healthUrl: str | None = None
    systemUrl: str | None = None
    token: str | None = None
    tags: list[str] | None = None
    enabled: bool | None = None
    pollingHealth: int | None = Field(None, ge=30)
    pollingSystem: int | None = Field(None, ge=30)
    pollingUpdates: int | None = Field(None, ge=300)
    pollingReboot: int | None = Field(None, ge=60)
    sslCheckUrl: str | None = None
    pollingSsl: int | None = Field(None, ge=300)
    teamsWebhookUrl: str | None = None
    serverLabel: str | None = Field(None, max_length=255)
    environment: str | None = Field(None, max_length=100)
    verifySSL: bool | None = None
    ip: str | None = Field(None, max_length=45)
    expectedMeta: dict[str, MetaValue] | None = None


class SiteResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    healthUrl: str | None = None
    systemUrl: str | None = None
    token: str | None = None
    tags: list[str] | None = None
    enabled: bool
    pollingHealth: int
    pollingSystem: int
    pollingUpdates: int
    pollingReboot: int
    sslCheckUrl: str | None = None
    pollingSsl: int
    teamsWebhookUrl: str | None = None
    serverLabel: str | None = None
    environment: str | None = None
    verifySSL: bool = True
    ip: str | None = None
    expectedMeta: dict[str, MetaValue] | None = None
    createdAt: datetime
    updatedAt: datetime

    model_config = {"from_attributes": True}


class SiteSnapshotResponse(BaseModel):
    id: str
    siteId: str
    snapshotType: str
    status: str | None = None
    rawData: dict[str, Any] | None = None
    metaMismatches: list[str] | None = None
    error: str | None = None
    polledAt: datetime

    model_config = {"from_attributes": True}


class PaginatedSiteSnapshotResponse(BaseModel):
    items: list[SiteSnapshotResponse]
    total: int


class SiteStatusResponse(BaseModel):
    """Current status of a site — latest snapshot of each type."""

    site: SiteResponse
    healthSnapshot: SiteSnapshotResponse | None = None
    systemSnapshot: SiteSnapshotResponse | None = None
    sslSnapshot: SiteSnapshotResponse | None = None


class PollResponse(BaseModel):
    message: str


class MonitorConfigResponse(BaseModel):
    checkIntervalSeconds: int
    livePollIntervalSeconds: int
    liveModeTtlSeconds: int
    uiBackgroundRefetchSeconds: int
    uiActiveRefetchSeconds: int
    heartbeatIntervalSeconds: int
