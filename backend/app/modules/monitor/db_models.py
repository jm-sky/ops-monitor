"""SQLAlchemy models for monitor module.

SiteDB     — reflects the `sites` table (created in migration 055).
SiteSnapshotDB — polling results (migration 056).
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SiteDB(Base):
    __tablename__ = "sites"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    health_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    system_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    token: Mapped[str | None] = mapped_column(String(500), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    polling_health: Mapped[int] = mapped_column(Integer, default=300, nullable=False)
    polling_system: Mapped[int] = mapped_column(Integer, default=300, nullable=False)
    polling_updates: Mapped[int] = mapped_column(Integer, default=43200, nullable=False)
    polling_reboot: Mapped[int] = mapped_column(Integer, default=1800, nullable=False)
    teams_webhook_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    server_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    environment: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(Text()), nullable=True)
    verify_ssl: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def to_response(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "healthUrl": self.health_url,
            "systemUrl": self.system_url,
            "token": self.token,
            "enabled": self.enabled,
            "pollingHealth": self.polling_health,
            "pollingSystem": self.polling_system,
            "pollingUpdates": self.polling_updates,
            "pollingReboot": self.polling_reboot,
            "teamsWebhookUrl": self.teams_webhook_url,
            "serverLabel": self.server_label,
            "environment": self.environment,
            "tags": self.tags,
            "verifySSL": self.verify_ssl,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class SiteSnapshotDB(Base):
    __tablename__ = "site_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    site_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sites.id", ondelete="CASCADE"),
        nullable=False,
    )
    snapshot_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # 'health' | 'system'
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    raw_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    polled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    __table_args__ = (
        Index(
            "ix_site_snapshots_site_type_polled",
            "site_id",
            "snapshot_type",
            "polled_at",
        ),
    )

    def to_response(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "siteId": str(self.site_id),
            "snapshotType": self.snapshot_type,
            "status": self.status,
            "rawData": self.raw_data,
            "error": self.error,
            "polledAt": self.polled_at,
        }
