"""SQLAlchemy model for package update events (migration 069)."""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PackageUpdateEventDB(Base):
    """One apt transaction (a ``history.log`` block) reported by a site's agent."""

    __tablename__ = "package_update_events"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    commandline: Mapped[str | None] = mapped_column(Text, nullable=True)
    requested_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    automatic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # {"install": [...], "upgrade": [...], "remove": [...], "purge": [...]} — see agent/README.md
    packages: Mapped[dict[str, Any]] = mapped_column(JSONB().with_variant(JSON(), "sqlite"), nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    __table_args__ = (
        UniqueConstraint("site_id", "started_at", name="uq_package_update_events_site_started"),
        Index("ix_package_update_events_started_at", "started_at"),
    )
