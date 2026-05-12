"""Pydantic schemas for monitor module API."""

from datetime import datetime
from typing import Any, Optional, Union

from pydantic import BaseModel, Field

MetaValue = Union[str, int, float, bool]


class SiteCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    healthUrl: Optional[str] = None
    systemUrl: Optional[str] = None
    token: Optional[str] = None
    tags: Optional[list[str]] = None
    enabled: bool = True
    pollingHealth: int = Field(300, ge=30)
    pollingSystem: int = Field(300, ge=30)
    pollingUpdates: int = Field(43200, ge=300)
    pollingReboot: int = Field(1800, ge=60)
    teamsWebhookUrl: Optional[str] = None
    serverLabel: Optional[str] = Field(None, max_length=255)
    environment: Optional[str] = Field(None, max_length=100)
    verifySSL: bool = True
    ip: Optional[str] = Field(None, max_length=45)
    expectedMeta: Optional[dict[str, MetaValue]] = None


class SiteUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    healthUrl: Optional[str] = None
    systemUrl: Optional[str] = None
    token: Optional[str] = None
    tags: Optional[list[str]] = None
    enabled: Optional[bool] = None
    pollingHealth: Optional[int] = Field(None, ge=30)
    pollingSystem: Optional[int] = Field(None, ge=30)
    pollingUpdates: Optional[int] = Field(None, ge=300)
    pollingReboot: Optional[int] = Field(None, ge=60)
    teamsWebhookUrl: Optional[str] = None
    serverLabel: Optional[str] = Field(None, max_length=255)
    environment: Optional[str] = Field(None, max_length=100)
    verifySSL: Optional[bool] = None
    ip: Optional[str] = Field(None, max_length=45)
    expectedMeta: Optional[dict[str, MetaValue]] = None


class SiteResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    healthUrl: Optional[str] = None
    systemUrl: Optional[str] = None
    token: Optional[str] = None
    tags: Optional[list[str]] = None
    enabled: bool
    pollingHealth: int
    pollingSystem: int
    pollingUpdates: int
    pollingReboot: int
    teamsWebhookUrl: Optional[str] = None
    serverLabel: Optional[str] = None
    environment: Optional[str] = None
    verifySSL: bool = True
    ip: Optional[str] = None
    expectedMeta: Optional[dict[str, MetaValue]] = None
    createdAt: datetime
    updatedAt: datetime

    model_config = {"from_attributes": True}


class SiteSnapshotResponse(BaseModel):
    id: str
    siteId: str
    snapshotType: str
    status: Optional[str] = None
    rawData: Optional[dict[str, Any]] = None
    metaMismatches: Optional[list[str]] = None
    error: Optional[str] = None
    polledAt: datetime

    model_config = {"from_attributes": True}


class PaginatedSiteSnapshotResponse(BaseModel):
    items: list[SiteSnapshotResponse]
    total: int


class SiteStatusResponse(BaseModel):
    """Current status of a site — latest snapshot of each type."""

    site: SiteResponse
    healthSnapshot: Optional[SiteSnapshotResponse] = None
    systemSnapshot: Optional[SiteSnapshotResponse] = None


class PollResponse(BaseModel):
    message: str


class MonitorConfigResponse(BaseModel):
    checkIntervalSeconds: int
    livePollIntervalSeconds: int
    liveModeTtlSeconds: int
    uiBackgroundRefetchSeconds: int
    uiActiveRefetchSeconds: int
    heartbeatIntervalSeconds: int
