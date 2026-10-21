"""Pydantic schemas for the package updates API."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class PackageUpdateEventResponse(BaseModel):
    id: str
    siteId: str
    siteName: str
    serverLabel: str | None = None
    # Hostname taken from the site's system/health URL (not the optional IP override).
    host: str | None = None
    startedAt: datetime
    finishedAt: datetime | None = None
    durationSeconds: int | None = None
    commandline: str | None = None
    requestedBy: str | None = None
    automatic: bool
    packages: dict[str, Any]


class PaginatedPackageUpdateResponse(BaseModel):
    items: list[PackageUpdateEventResponse]
    total: int
