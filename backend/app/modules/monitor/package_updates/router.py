"""Package update history endpoints: API-key read for external tools, JWT read for the UI."""

import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import CurrentUser

from ..api_keys.db_models import SCOPE_READ_PACKAGE_UPDATES, ApiKeyDB
from ..api_keys.dependencies import require_api_key_scope
from ..repositories import SiteRepository
from .repositories import PackageUpdateRepository, get_package_update_repository
from .schemas import PaginatedPackageUpdateResponse
from .service import to_event_response

router = APIRouter()

_MAX_LIMIT = 1000


def _as_utc(value: datetime | None) -> datetime | None:
    """Treat naive query datetimes as UTC."""
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


async def _query(
    repository: PackageUpdateRepository,
    *,
    site_id: uuid.UUID | None,
    from_: datetime | None,
    to: datetime | None,
    include_automatic: bool,
    limit: int,
    offset: int,
) -> PaginatedPackageUpdateResponse:
    started_from, started_to = _as_utc(from_), _as_utc(to)
    if started_from and started_to and started_from > started_to:
        raise HTTPException(status_code=422, detail="'from' must not be after 'to'")
    rows, total = await repository.query(
        site_id=site_id,
        started_from=started_from,
        started_to=started_to,
        include_automatic=include_automatic,
        limit=limit,
        offset=offset,
    )
    return PaginatedPackageUpdateResponse(items=[to_event_response(event, site) for event, site in rows], total=total)


@router.get(
    "/package-updates",
    response_model=PaginatedPackageUpdateResponse,
    summary="Package update events across servers (API key with scope read:package-updates)",
)
async def list_package_updates(
    _: Annotated[ApiKeyDB, Depends(require_api_key_scope(SCOPE_READ_PACKAGE_UPDATES))],
    repository: Annotated[PackageUpdateRepository, Depends(get_package_update_repository)],
    from_: Annotated[datetime | None, Query(alias="from", description="started_at >= from (ISO 8601; naive = UTC)")] = None,
    to: Annotated[datetime | None, Query(description="started_at <= to (ISO 8601; naive = UTC)")] = None,
    site_id: uuid.UUID | None = None,
    include_automatic: bool = False,
    limit: Annotated[int, Query(ge=1, le=_MAX_LIMIT)] = 200,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> PaginatedPackageUpdateResponse:
    return await _query(repository, site_id=site_id, from_=from_, to=to, include_automatic=include_automatic, limit=limit, offset=offset)


@router.get(
    "/sites/{site_id}/package-updates",
    response_model=PaginatedPackageUpdateResponse,
    summary="Package update events of one site (logged-in user)",
)
async def list_site_package_updates(
    site_id: uuid.UUID,
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    repository: Annotated[PackageUpdateRepository, Depends(get_package_update_repository)],
    include_automatic: bool = False,
    limit: Annotated[int, Query(ge=1, le=_MAX_LIMIT)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> PaginatedPackageUpdateResponse:
    if not await SiteRepository(db).get_by_id(site_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
    return await _query(repository, site_id=site_id, from_=None, to=None, include_automatic=include_automatic, limit=limit, offset=offset)
