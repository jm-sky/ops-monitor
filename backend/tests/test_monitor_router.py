"""Tests for monitor router endpoints."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from dataclasses import dataclass
from datetime import UTC, datetime

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.core.csrf import CSRF_COOKIE_NAME, CSRF_HEADER_NAME
from app.modules.auth.dependencies import get_current_user, require_admin
from app.modules.monitor.repositories import SiteRepository, SnapshotRepository
from main import app


def _csrf_headers(client: TestClient) -> dict[str, str]:
    response = client.get("/api/auth/csrf-token")
    assert response.status_code == status.HTTP_200_OK
    token = response.cookies.get(CSRF_COOKIE_NAME) or response.json()["csrf_token"]
    return {CSRF_HEADER_NAME: token}


class _FakeUser:
    isAdmin = True
    isOwner = False
    isPremium = False
    isActive = True
    isEmailVerified = True


class _FakeNonAdminUser:
    isAdmin = False
    isOwner = False
    isPremium = False
    isActive = True
    isEmailVerified = True


@dataclass
class _FakeSite:
    id: uuid.UUID
    name: str
    health_url: str | None = None
    system_url: str | None = None
    ssl_check_url: str | None = None
    token: str | None = None
    teams_webhook_url: str | None = None

    def to_response(self) -> dict[str, object]:
        now = datetime.now(UTC)
        return {
            "id": str(self.id),
            "name": self.name,
            "description": None,
            "healthUrl": self.health_url,
            "systemUrl": self.system_url,
            "token": self.token,
            "tags": None,
            "enabled": True,
            "pollingHealth": 300,
            "pollingSystem": 300,
            "pollingUpdates": 43200,
            "pollingReboot": 1800,
            "sslCheckUrl": self.ssl_check_url,
            "pollingSsl": 43200,
            "teamsWebhookUrl": self.teams_webhook_url,
            "serverLabel": None,
            "environment": None,
            "verifySSL": True,
            "createdAt": now,
            "updatedAt": now,
        }


@dataclass
class _FakeSnapshot:
    site_id: uuid.UUID
    snapshot_type: str
    status: str

    def to_response(self) -> dict[str, object]:
        return {
            "id": str(uuid.uuid4()),
            "siteId": str(self.site_id),
            "snapshotType": self.snapshot_type,
            "status": self.status,
            "rawData": {"status": self.status},
            "error": None,
            "polledAt": datetime.now(UTC),
        }


@pytest.fixture
def monitor_client() -> Generator[TestClient, None, None]:
    """Test client with monitor auth dependencies overridden."""

    async def _mock_current_user() -> _FakeUser:
        return _FakeUser()

    async def _mock_require_admin() -> _FakeUser:
        return _FakeUser()

    app.dependency_overrides[get_current_user] = _mock_current_user
    app.dependency_overrides[require_admin] = _mock_require_admin
    with TestClient(app) as client:
        try:
            yield client
        finally:
            app.dependency_overrides.pop(get_current_user, None)
            app.dependency_overrides.pop(require_admin, None)


@pytest.fixture
def non_admin_monitor_client() -> Generator[TestClient, None, None]:
    """Test client authenticated as a non-admin user (no require_admin override)."""

    async def _mock_current_user() -> _FakeNonAdminUser:
        return _FakeNonAdminUser()

    app.dependency_overrides[get_current_user] = _mock_current_user
    with TestClient(app) as client:
        try:
            yield client
        finally:
            app.dependency_overrides.pop(get_current_user, None)


def test_list_site_statuses_returns_latest_snapshots(
    monitor_client: TestClient,
) -> None:
    """It returns one entry per site and only latest health/system snapshots."""
    site_a = _FakeSite(
        id=uuid.uuid4(),
        name="site-a",
        health_url="https://a.example/health",
        system_url="https://a.example/system",
    )
    site_b = _FakeSite(
        id=uuid.uuid4(),
        name="site-b",
        health_url="https://b.example/health",
    )

    async def _mock_get_all(_: SiteRepository) -> list[_FakeSite]:
        return [site_a, site_b]

    async def _mock_get_latest_for_sites(_: SnapshotRepository, __: list[uuid.UUID]) -> dict[uuid.UUID, dict[str, _FakeSnapshot]]:
        return {
            site_a.id: {
                "health": _FakeSnapshot(
                    site_id=site_a.id,
                    snapshot_type="health",
                    status="ok",
                ),
                "system": _FakeSnapshot(
                    site_id=site_a.id,
                    snapshot_type="system",
                    status="reboot_required",
                ),
            },
            site_b.id: {
                "health": _FakeSnapshot(
                    site_id=site_b.id,
                    snapshot_type="health",
                    status="degraded",
                )
            },
        }

    original_get_all = SiteRepository.get_all
    original_get_latest_for_sites = SnapshotRepository.get_latest_for_sites
    SiteRepository.get_all = _mock_get_all  # type: ignore[method-assign, assignment]
    SnapshotRepository.get_latest_for_sites = _mock_get_latest_for_sites  # type: ignore[method-assign, assignment]

    try:
        response = monitor_client.get("/api/monitor/site-statuses")
    finally:
        SiteRepository.get_all = original_get_all  # type: ignore[method-assign]
        SnapshotRepository.get_latest_for_sites = original_get_latest_for_sites  # type: ignore[method-assign]

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2

    by_name = {item["site"]["name"]: item for item in payload}
    assert by_name["site-a"]["healthSnapshot"]["status"] == "ok"
    assert by_name["site-a"]["systemSnapshot"]["status"] == "reboot_required"
    assert by_name["site-b"]["healthSnapshot"]["status"] == "degraded"
    assert by_name["site-b"]["systemSnapshot"] is None


def test_list_site_statuses_omits_orphan_health_snapshot(
    monitor_client: TestClient,
) -> None:
    """Health snapshot is hidden when the site has no health URL configured."""
    site = _FakeSite(
        id=uuid.uuid4(),
        name="server-only",
        system_url="https://example.com/system",
    )

    async def _mock_get_all(_: SiteRepository) -> list[_FakeSite]:
        return [site]

    async def _mock_get_latest_for_sites(_: SnapshotRepository, __: list[uuid.UUID]) -> dict[uuid.UUID, dict[str, _FakeSnapshot]]:
        return {
            site.id: {
                "health": _FakeSnapshot(
                    site_id=site.id,
                    snapshot_type="health",
                    status="failed",
                ),
                "system": _FakeSnapshot(
                    site_id=site.id,
                    snapshot_type="system",
                    status="up_to_date",
                ),
            },
        }

    original_get_all = SiteRepository.get_all
    original_get_latest_for_sites = SnapshotRepository.get_latest_for_sites
    SiteRepository.get_all = _mock_get_all  # type: ignore[method-assign, assignment]
    SnapshotRepository.get_latest_for_sites = _mock_get_latest_for_sites  # type: ignore[method-assign, assignment]

    try:
        response = monitor_client.get("/api/monitor/site-statuses")
    finally:
        SiteRepository.get_all = original_get_all  # type: ignore[method-assign]
        SnapshotRepository.get_latest_for_sites = original_get_latest_for_sites  # type: ignore[method-assign]

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["healthSnapshot"] is None
    assert payload[0]["systemSnapshot"]["status"] == "up_to_date"


def test_list_site_statuses_includes_ssl_snapshot(
    monitor_client: TestClient,
) -> None:
    """Site with sslCheckUrl returns sslSnapshot in /site-statuses."""
    site = _FakeSite(
        id=uuid.uuid4(),
        name="site-with-cert",
        ssl_check_url="https://example.com",
    )

    async def _mock_get_all(_: SiteRepository) -> list[_FakeSite]:
        return [site]

    async def _mock_get_latest_for_sites(_: SnapshotRepository, __: list[uuid.UUID]) -> dict[uuid.UUID, dict[str, _FakeSnapshot]]:
        return {
            site.id: {
                "ssl": _FakeSnapshot(
                    site_id=site.id,
                    snapshot_type="ssl",
                    status="expiring_soon",
                ),
            },
        }

    original_get_all = SiteRepository.get_all
    original_get_latest_for_sites = SnapshotRepository.get_latest_for_sites
    SiteRepository.get_all = _mock_get_all  # type: ignore[method-assign, assignment]
    SnapshotRepository.get_latest_for_sites = _mock_get_latest_for_sites  # type: ignore[method-assign, assignment]

    try:
        response = monitor_client.get("/api/monitor/site-statuses")
    finally:
        SiteRepository.get_all = original_get_all  # type: ignore[method-assign]
        SnapshotRepository.get_latest_for_sites = original_get_latest_for_sites  # type: ignore[method-assign]

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["sslSnapshot"]["status"] == "expiring_soon"


def test_update_site_clearing_health_url_deletes_health_snapshots(
    monitor_client: TestClient,
) -> None:
    """Clearing healthUrl removes stored health snapshots for the site."""
    site_id = uuid.uuid4()
    site = _FakeSite(
        id=site_id,
        name="server",
        health_url="https://example.com/health",
        system_url="https://example.com/system",
    )
    deleted_types: list[str] = []

    async def _mock_get_by_id(_: SiteRepository, sid: uuid.UUID) -> _FakeSite | None:
        return site if sid == site_id else None

    async def _mock_update(_: SiteRepository, current_site: _FakeSite, data: dict[str, object]) -> _FakeSite:
        for key, value in data.items():
            setattr(current_site, key, value)
        return current_site

    async def _mock_delete_all_for_type(_: SnapshotRepository, sid: uuid.UUID, snapshot_type: str) -> None:
        deleted_types.append(snapshot_type)

    original_get_by_id = SiteRepository.get_by_id
    original_update = SiteRepository.update
    original_delete_all = SnapshotRepository.delete_all_for_type
    SiteRepository.get_by_id = _mock_get_by_id  # type: ignore[method-assign, assignment]
    SiteRepository.update = _mock_update  # type: ignore[method-assign, assignment]
    SnapshotRepository.delete_all_for_type = _mock_delete_all_for_type  # type: ignore[method-assign, assignment]

    try:
        response = monitor_client.put(
            f"/api/monitor/sites/{site_id}",
            json={"healthUrl": None},
            headers=_csrf_headers(monitor_client),
        )
    finally:
        SiteRepository.get_by_id = original_get_by_id  # type: ignore[method-assign]
        SiteRepository.update = original_update  # type: ignore[method-assign]
        SnapshotRepository.delete_all_for_type = original_delete_all  # type: ignore[method-assign]

    assert response.status_code == 200
    assert deleted_types == ["health"]


def test_non_admin_does_not_see_site_secrets_in_site_statuses(
    non_admin_monitor_client: TestClient,
) -> None:
    """Regression test for SEC-1 (2026-07-20): a non-admin, authenticated
    user must not see the polling bearer token or Teams webhook URL for
    monitored sites — those are credentials, not display data."""
    site = _FakeSite(
        id=uuid.uuid4(),
        name="secret-site",
        health_url="https://example.com/health",
        token="super-secret-polling-token",
        teams_webhook_url="https://outlook.office.com/webhook/secret",
    )

    async def _mock_get_all(_: SiteRepository) -> list[_FakeSite]:
        return [site]

    async def _mock_get_latest_for_sites(_: SnapshotRepository, __: list[uuid.UUID]) -> dict[uuid.UUID, dict[str, _FakeSnapshot]]:
        return {}

    original_get_all = SiteRepository.get_all
    original_get_latest_for_sites = SnapshotRepository.get_latest_for_sites
    SiteRepository.get_all = _mock_get_all  # type: ignore[method-assign, assignment]
    SnapshotRepository.get_latest_for_sites = _mock_get_latest_for_sites  # type: ignore[method-assign, assignment]

    try:
        response = non_admin_monitor_client.get("/api/monitor/site-statuses")
    finally:
        SiteRepository.get_all = original_get_all  # type: ignore[method-assign]
        SnapshotRepository.get_latest_for_sites = original_get_latest_for_sites  # type: ignore[method-assign]

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["site"]["token"] is None
    assert payload[0]["site"]["teamsWebhookUrl"] is None


def test_admin_still_sees_site_secrets_in_site_statuses(
    monitor_client: TestClient,
) -> None:
    """Admins still need the real token/webhook to manage sites."""
    site = _FakeSite(
        id=uuid.uuid4(),
        name="secret-site",
        health_url="https://example.com/health",
        token="super-secret-polling-token",
        teams_webhook_url="https://outlook.office.com/webhook/secret",
    )

    async def _mock_get_all(_: SiteRepository) -> list[_FakeSite]:
        return [site]

    async def _mock_get_latest_for_sites(_: SnapshotRepository, __: list[uuid.UUID]) -> dict[uuid.UUID, dict[str, _FakeSnapshot]]:
        return {}

    original_get_all = SiteRepository.get_all
    original_get_latest_for_sites = SnapshotRepository.get_latest_for_sites
    SiteRepository.get_all = _mock_get_all  # type: ignore[method-assign, assignment]
    SnapshotRepository.get_latest_for_sites = _mock_get_latest_for_sites  # type: ignore[method-assign, assignment]

    try:
        response = monitor_client.get("/api/monitor/site-statuses")
    finally:
        SiteRepository.get_all = original_get_all  # type: ignore[method-assign]
        SnapshotRepository.get_latest_for_sites = original_get_latest_for_sites  # type: ignore[method-assign]

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["site"]["token"] == "super-secret-polling-token"
    assert payload[0]["site"]["teamsWebhookUrl"] == "https://outlook.office.com/webhook/secret"
