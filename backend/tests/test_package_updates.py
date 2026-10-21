"""Tests for package update history: dedup, agent sync, API keys and the read endpoints."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import patch

import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.pool import StaticPool

from app.core.csrf import CSRF_COOKIE_NAME, CSRF_HEADER_NAME
from app.core.database import Base, get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.monitor.api_keys.db_models import SCOPE_READ_PACKAGE_UPDATES, ApiKeyDB
from app.modules.monitor.api_keys.repositories import ApiKeyRepository
from app.modules.monitor.api_keys.service import ApiKeyService, InvalidScopeError, hash_api_key
from app.modules.monitor.db_models import SiteDB
from app.modules.monitor.package_updates import service as sync_module
from app.modules.monitor.package_updates.db_models import PackageUpdateEventDB
from app.modules.monitor.package_updates.repositories import PackageUpdateRepository
from app.modules.monitor.package_updates.service import PackageHistorySyncService, build_history_url, normalize_events
from main import app


@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(*_: Any, **__: Any) -> str:
    return "JSON"


@compiles(ARRAY, "sqlite")
def _compile_array_sqlite(*_: Any, **__: Any) -> str:
    return "JSON"


T0 = datetime(2026, 7, 1, 9, 0, tzinfo=UTC)


def _event(offset_hours: int, *, automatic: bool = False, finished: bool = True) -> dict[str, Any]:
    start = T0 + timedelta(hours=offset_hours)
    return {
        "started_at": start.isoformat(),
        "finished_at": (start + timedelta(seconds=90)).isoformat() if finished else None,
        "commandline": "apt upgrade" if not automatic else "/usr/bin/unattended-upgrade",
        "requested_by": None if automatic else "jan (1000)",
        "automatic": automatic,
        "packages": {"upgrade": [{"name": "curl", "arch": "amd64", "from_version": "1", "to_version": "2", "auto_installed": False}]},
    }


@pytest_asyncio.fixture
async def session_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=[SiteDB.__table__, ApiKeyDB.__table__, PackageUpdateEventDB.__table__])
    yield async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    await engine.dispose()


@pytest_asyncio.fixture
async def site(session_factory: async_sessionmaker[AsyncSession]) -> SiteDB:
    async with session_factory() as db:
        row = SiteDB(
            id=uuid.uuid4(),
            name="bsm-api01",
            system_url="https://bsm-api01.example.local:9100/system",
            token="agent-secret",
            server_label="API 01",
            verify_ssl=True,
            enabled=True,
        )
        db.add(row)
        await db.commit()
    return row


async def _store(session_factory: async_sessionmaker[AsyncSession], site_id: uuid.UUID, raw: list[dict[str, Any]]) -> int:
    async with session_factory() as db:
        return await PackageUpdateRepository(db).insert_ignore_duplicates(site_id, normalize_events(raw))


# --- parsing / URL ----------------------------------------------------------


def test_build_history_url_replaces_system_path() -> None:
    assert build_history_url("https://h:9100/system") == "https://h:9100/package-history"
    assert build_history_url("https://h/agent/system/?x=1") == "https://h/agent/package-history"
    assert build_history_url("https://h/metrics") is None


def test_normalize_events_drops_malformed_and_duplicate_starts() -> None:
    good = _event(0)
    events = normalize_events([good, {**good, "commandline": "dup"}, {"started_at": "nope"}, "x", {"packages": {}}, {**_event(1), "packages": "bad"}])

    assert len(events) == 2
    assert events[1]["packages"] == {}
    assert normalize_events(None) == []


def test_normalize_events_assumes_utc_for_naive_dates() -> None:
    event = normalize_events([{"started_at": "2026-07-01T09:00:00"}])[0]
    assert event["started_at"].tzinfo is not None


# --- dedup ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_insert_skips_duplicates(session_factory: async_sessionmaker[AsyncSession], site: SiteDB) -> None:
    assert await _store(session_factory, site.id, [_event(0), _event(1)]) == 2
    assert await _store(session_factory, site.id, [_event(0), _event(1)]) == 0
    assert await _store(session_factory, site.id, [_event(1), _event(2, finished=False)]) == 1

    async with session_factory() as db:
        rows, total = await PackageUpdateRepository(db).query(include_automatic=True)
    assert total == 3
    assert rows[0][0].finished_at is None  # newest first; missing End-Date preserved


@pytest.mark.asyncio
async def test_same_start_time_allowed_for_different_sites(session_factory: async_sessionmaker[AsyncSession], site: SiteDB) -> None:
    async with session_factory() as db:
        other = SiteDB(id=uuid.uuid4(), name="other", enabled=True, verify_ssl=True)
        db.add(other)
        await db.commit()

    assert await _store(session_factory, site.id, [_event(0)]) == 1
    assert await _store(session_factory, other.id, [_event(0)]) == 1


@pytest.mark.asyncio
async def test_latest_started_at(session_factory: async_sessionmaker[AsyncSession], site: SiteDB) -> None:
    async with session_factory() as db:
        assert await PackageUpdateRepository(db).get_latest_started_at(site.id) is None
    await _store(session_factory, site.id, [_event(0), _event(5)])
    async with session_factory() as db:
        latest = await PackageUpdateRepository(db).get_latest_started_at(site.id)
    assert latest is not None
    assert latest.replace(tzinfo=UTC) == T0 + timedelta(hours=5)


# --- agent sync -------------------------------------------------------------


class _FakeAgent:
    """Stands in for httpx.AsyncClient; records requests and replays queued events."""

    def __init__(self, events: list[dict[str, Any]], status_code: int = 200) -> None:
        self.events = events
        self.status_code = status_code
        self.requests: list[tuple[str, dict[str, str], dict[str, str] | None]] = []

    def __call__(self, **_: Any) -> _FakeAgent:
        return self

    async def __aenter__(self) -> _FakeAgent:
        return self

    async def __aexit__(self, *_: object) -> None:
        pass

    async def get(self, url: str, headers: dict[str, str], params: dict[str, str] | None = None) -> httpx.Response:
        self.requests.append((url, headers, params))
        request = httpx.Request("GET", url)
        return httpx.Response(self.status_code, json={"events": self.events}, request=request)


@pytest.mark.asyncio
async def test_sync_stores_events_and_requests_from_last_started_at(session_factory: async_sessionmaker[AsyncSession], site: SiteDB) -> None:
    agent = _FakeAgent([_event(0), _event(1, automatic=True)])
    with patch.object(sync_module, "AsyncSessionLocal", session_factory), patch.object(sync_module.httpx, "AsyncClient", agent):
        service = PackageHistorySyncService()
        assert await service.sync_site(site) == 2

        # Agent re-sends the boundary event (since is inclusive) plus one new one.
        agent.events = [_event(1, automatic=True), _event(2)]
        assert await service.sync_site(site) == 1

    first, second = agent.requests
    assert first[0] == "https://bsm-api01.example.local:9100/package-history"
    assert first[1]["Authorization"] == "Bearer agent-secret"
    assert first[2] is None
    assert datetime.fromisoformat(second[2]["since"] if second[2] else "") == T0 + timedelta(hours=1)

    async with session_factory() as db:
        _, total = await PackageUpdateRepository(db).query(include_automatic=True)
    assert total == 3


@pytest.mark.asyncio
async def test_sync_propagates_agent_errors(session_factory: async_sessionmaker[AsyncSession], site: SiteDB) -> None:
    agent = _FakeAgent([], status_code=404)
    with patch.object(sync_module, "AsyncSessionLocal", session_factory), patch.object(sync_module.httpx, "AsyncClient", agent):
        with pytest.raises(httpx.HTTPStatusError):
            await PackageHistorySyncService().sync_site(site)


@pytest.mark.asyncio
async def test_monitor_service_swallows_sync_errors(site: SiteDB) -> None:
    from app.modules.monitor.service import MonitorService

    with patch.object(PackageHistorySyncService, "sync_site", side_effect=RuntimeError("boom")):
        await MonitorService()._sync_package_history(site)  # must not raise


# --- API keys ---------------------------------------------------------------


@pytest.mark.asyncio
async def test_api_key_is_stored_hashed_and_authenticates(session_factory: async_sessionmaker[AsyncSession]) -> None:
    async with session_factory() as db:
        service = ApiKeyService(ApiKeyRepository(db))
        row, plaintext = await service.create("worklog", [SCOPE_READ_PACKAGE_UPDATES], created_by="u1")

        assert plaintext.startswith("opsm_")
        assert plaintext not in (row.key_hash, row.key_prefix)
        assert row.key_hash == hash_api_key(plaintext)
        assert (await service.authenticate(plaintext, SCOPE_READ_PACKAGE_UPDATES)) is not None
        assert row.last_used_at is not None


@pytest.mark.asyncio
async def test_api_key_rejections(session_factory: async_sessionmaker[AsyncSession]) -> None:
    async with session_factory() as db:
        repo = ApiKeyRepository(db)
        service = ApiKeyService(repo)
        _, plaintext = await service.create("k", [SCOPE_READ_PACKAGE_UPDATES], created_by=None)
        _, expired = await service.create("old", [SCOPE_READ_PACKAGE_UPDATES], created_by=None, expires_at=datetime.now(UTC) - timedelta(days=1))
        revoked_row, revoked = await service.create("gone", [SCOPE_READ_PACKAGE_UPDATES], created_by=None)
        await repo.revoke(revoked_row)

        assert await service.authenticate(plaintext + "x", SCOPE_READ_PACKAGE_UPDATES) is None
        assert await service.authenticate("not-a-key", SCOPE_READ_PACKAGE_UPDATES) is None
        assert await service.authenticate(plaintext, "write:everything") is None
        assert await service.authenticate(expired, SCOPE_READ_PACKAGE_UPDATES) is None
        assert await service.authenticate(revoked, SCOPE_READ_PACKAGE_UPDATES) is None


@pytest.mark.asyncio
async def test_unknown_scope_is_rejected(session_factory: async_sessionmaker[AsyncSession]) -> None:
    async with session_factory() as db:
        with pytest.raises(InvalidScopeError):
            await ApiKeyService(ApiKeyRepository(db)).create("k", ["admin:all"], created_by=None)


# --- endpoints --------------------------------------------------------------


class _FakeUser:
    isAdmin = False
    isOwner = False
    isActive = True


@pytest_asyncio.fixture
async def api(session_factory: async_sessionmaker[AsyncSession]) -> AsyncIterator[httpx.AsyncClient]:
    async def _get_db() -> AsyncIterator[AsyncSession]:
        async with session_factory() as db:
            yield db

    async def _user() -> _FakeUser:
        return _FakeUser()

    app.dependency_overrides[get_db] = _get_db
    app.dependency_overrides[get_current_user] = _user
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as client:
        csrf = await client.get("/api/auth/csrf-token")  # unsafe methods need the double-submit token
        client.headers[CSRF_HEADER_NAME] = csrf.cookies.get(CSRF_COOKIE_NAME) or csrf.json()["csrf_token"]
        yield client
    app.dependency_overrides.clear()


async def _make_key(session_factory: async_sessionmaker[AsyncSession], scopes: list[str] | None = None) -> str:
    async with session_factory() as db:
        row, plaintext = await ApiKeyService(ApiKeyRepository(db)).create("worklog", scopes or [SCOPE_READ_PACKAGE_UPDATES], created_by=None)
        if scopes == []:
            row.scopes = []
            await db.commit()
    return plaintext


@pytest.mark.asyncio
async def test_endpoint_requires_api_key(api: httpx.AsyncClient, session_factory: async_sessionmaker[AsyncSession], site: SiteDB) -> None:
    assert (await api.get("/api/monitor/package-updates")).status_code == 401
    assert (await api.get("/api/monitor/package-updates", headers={"Authorization": "Bearer opsm_wrong"})).status_code == 401

    no_scope = await _make_key(session_factory, scopes=[])
    assert (await api.get("/api/monitor/package-updates", headers={"Authorization": f"Bearer {no_scope}"})).status_code == 401


@pytest.mark.asyncio
async def test_endpoint_returns_events_with_server_name_and_host(api: httpx.AsyncClient, session_factory: async_sessionmaker[AsyncSession], site: SiteDB) -> None:
    await _store(session_factory, site.id, [_event(0), _event(1, automatic=True), _event(2, finished=False)])
    headers = {"Authorization": f"Bearer {await _make_key(session_factory)}"}

    body = (await api.get("/api/monitor/package-updates", headers=headers)).json()

    assert body["total"] == 2  # automatic excluded by default
    newest, oldest = body["items"]
    assert newest["finishedAt"] is None and newest["durationSeconds"] is None
    assert oldest["durationSeconds"] == 90
    assert oldest["siteName"] == "bsm-api01"
    assert oldest["host"] == "bsm-api01.example.local"
    assert oldest["serverLabel"] == "API 01"
    assert oldest["requestedBy"] == "jan (1000)"
    assert oldest["packages"]["upgrade"][0]["name"] == "curl"


@pytest.mark.asyncio
async def test_endpoint_filters(api: httpx.AsyncClient, session_factory: async_sessionmaker[AsyncSession], site: SiteDB) -> None:
    await _store(session_factory, site.id, [_event(0), _event(24, automatic=True), _event(48)])
    headers = {"Authorization": f"Bearer {await _make_key(session_factory)}"}

    with_auto = (await api.get("/api/monitor/package-updates", params={"include_automatic": "true"}, headers=headers)).json()
    assert with_auto["total"] == 3

    window = (await api.get("/api/monitor/package-updates", params={"from": (T0 + timedelta(hours=12)).isoformat(), "to": (T0 + timedelta(hours=72)).isoformat(), "include_automatic": "true"}, headers=headers)).json()
    assert window["total"] == 2

    other_site = (await api.get("/api/monitor/package-updates", params={"site_id": str(uuid.uuid4())}, headers=headers)).json()
    assert other_site == {"items": [], "total": 0}

    paged = (await api.get("/api/monitor/package-updates", params={"include_automatic": "true", "limit": 1, "offset": 1}, headers=headers)).json()
    assert paged["total"] == 3 and len(paged["items"]) == 1

    bad = await api.get("/api/monitor/package-updates", params={"from": "2026-08-01T00:00:00Z", "to": "2026-07-01T00:00:00Z"}, headers=headers)
    assert bad.status_code == 422


@pytest.mark.asyncio
async def test_site_endpoint_uses_user_auth(api: httpx.AsyncClient, session_factory: async_sessionmaker[AsyncSession], site: SiteDB) -> None:
    await _store(session_factory, site.id, [_event(0), _event(1, automatic=True)])

    response = await api.get(f"/api/monitor/sites/{site.id}/package-updates", params={"include_automatic": "true"})
    assert response.status_code == 200
    assert response.json()["total"] == 2

    assert (await api.get(f"/api/monitor/sites/{uuid.uuid4()}/package-updates")).status_code == 404


# --- admin key management ---------------------------------------------------


class _FakeAdmin(_FakeUser):
    id = "admin-1"
    isAdmin = True


@pytest.mark.asyncio
async def test_admin_creates_lists_and_revokes_keys(api: httpx.AsyncClient, session_factory: async_sessionmaker[AsyncSession], site: SiteDB) -> None:
    from app.modules.auth.dependencies import require_admin

    async def _admin() -> _FakeAdmin:
        return _FakeAdmin()

    app.dependency_overrides[require_admin] = _admin

    created = await api.post("/api/monitor/api-keys", json={"name": "worklog-automation", "scopes": [SCOPE_READ_PACKAGE_UPDATES]})
    assert created.status_code == 201
    body = created.json()
    assert body["key"].startswith("opsm_") and body["createdBy"] == "admin-1"

    listed = (await api.get("/api/monitor/api-keys")).json()
    assert len(listed) == 1 and "key" not in listed[0] and listed[0]["keyPrefix"] == body["key"][: len(listed[0]["keyPrefix"])]

    headers = {"Authorization": f"Bearer {body['key']}"}
    assert (await api.get("/api/monitor/package-updates", headers=headers)).status_code == 200

    assert (await api.delete(f"/api/monitor/api-keys/{body['id']}")).json()["revokedAt"] is not None
    assert (await api.get("/api/monitor/package-updates", headers=headers)).status_code == 401
    assert (await api.delete(f"/api/monitor/api-keys/{uuid.uuid4()}")).status_code == 404

    bad = await api.post("/api/monitor/api-keys", json={"name": "x", "scopes": ["admin:all"]})
    assert bad.status_code == 422


@pytest.mark.asyncio
async def test_non_admin_cannot_manage_keys(api: httpx.AsyncClient) -> None:
    assert (await api.post("/api/monitor/api-keys", json={"name": "x", "scopes": [SCOPE_READ_PACKAGE_UPDATES]})).status_code == 403
    assert (await api.get("/api/monitor/api-keys")).status_code == 403
