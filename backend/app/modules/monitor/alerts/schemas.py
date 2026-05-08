"""Pydantic schemas for alert channels API."""

import re
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

AlertType = Literal["health", "reboot", "updates"]
HealthSeverity = Literal["degraded", "failed"]

_HHMM_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


class QuietHoursConfig(BaseModel):
    enabled: bool = False
    start: str = "22:00"
    end: str = "07:00"
    timezone: str = "Europe/Warsaw"

    @field_validator("start", "end")
    @classmethod
    def _check_hhmm(cls, v: str) -> str:
        if not _HHMM_RE.match(v):
            raise ValueError("must be 'HH:MM' (24h)")
        return v


class AlertChannelFilters(BaseModel):
    alert_types: list[AlertType] = Field(default_factory=list)
    min_health_severity: HealthSeverity = "degraded"
    site_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    quiet_hours: QuietHoursConfig = Field(default_factory=QuietHoursConfig)
    re_alert_after_minutes: int | None = Field(default=None, ge=1)

    model_config = {"extra": "ignore"}


class AlertChannelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., pattern="^(teams|email|telegram)$")
    enabled: bool = True
    config: dict[str, Any] = Field(default_factory=dict)
    filters: AlertChannelFilters = Field(default_factory=AlertChannelFilters)


class AlertChannelUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    enabled: bool | None = None
    config: dict[str, Any] | None = None
    filters: AlertChannelFilters | None = None


class AlertChannelResponse(BaseModel):
    id: str
    name: str
    type: str
    enabled: bool
    config: dict[str, Any]
    filters: dict[str, Any]
    createdAt: datetime
    updatedAt: datetime

    model_config = {"from_attributes": True}


class TestAlertResponse(BaseModel):
    success: bool
    message: str


class AlertEventResponse(BaseModel):
    id: str
    siteId: str
    siteName: str
    channelId: str
    channelName: str
    alertType: str
    status: str
    sentAt: datetime
