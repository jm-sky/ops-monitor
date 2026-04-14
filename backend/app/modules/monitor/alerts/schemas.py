"""Pydantic schemas for alert channels API."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class AlertChannelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., pattern="^(teams|email|telegram)$")
    enabled: bool = True
    config: dict[str, Any] = Field(default_factory=dict)


class AlertChannelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    enabled: Optional[bool] = None
    config: Optional[dict[str, Any]] = None


class AlertChannelResponse(BaseModel):
    id: str
    name: str
    type: str
    enabled: bool
    config: dict[str, Any]
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
