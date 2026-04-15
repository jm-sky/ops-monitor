"""Tests for monitor router endpoints."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.modules.auth.dependencies import get_current_user, require_admin
from app.modules.monitor.repositories import SnapshotRepository, SiteRepository
from main import app


class _FakeUser:
    isAdmin = True
    isOwner = False
    isPremium = False
    isActive = True
    isEmailVerified = True


@dataclass
class _FakeSite:
    id: uuid.UUID
    name: str

    def to_response(self) -> dict[str, object]:
        now = datetime.now(UTC)
        return {
            "id": str(self.id),
            "name": self.name,
            "description": None,
            "healthUrl": None,
            "systemUrl": None,
            "token": None,
            "enabled": True,
            "pollingHealth": 300,
            "pollingSystem": 300,
            "pollingUpdates": 43200,
            "pollingReboot": 1800,
            "teamsWebhookUrl": None,
            "serverLabel": None,
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


def test_list_site_statuses_returns_latest_snapshots(monitor_client: TestClient) -> None:
    """It returns one entry per site and only latest health/system snapshots."""
    site_a = _FakeSite(id=uuid.uuid4(), name="site-a")
    site_b = _FakeSite(id=uuid.uuid4(), name="site-b")

    async def _mock_get_all(_: SiteRepository) -> list[_FakeSite]:
        return [site_a, site_b]

    async def _mock_get_latest_for_sites(
        _: SnapshotRepository, __: list[uuid.UUID]
    ) -> dict[uuid.UUID, dict[str, _FakeSnapshot]]:
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
    SiteRepository.get_all = _mock_get_all
    SnapshotRepository.get_latest_for_sites = _mock_get_latest_for_sites

    try:
        response = monitor_client.get("/api/monitor/site-statuses")
    finally:
        SiteRepository.get_all = original_get_all
        SnapshotRepository.get_latest_for_sites = original_get_latest_for_sites

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2

    by_name = {item["site"]["name"]: item for item in payload}
    assert by_name["site-a"]["healthSnapshot"]["status"] == "ok"
    assert by_name["site-a"]["systemSnapshot"]["status"] == "reboot_required"
    assert by_name["site-b"]["healthSnapshot"]["status"] == "degraded"
    assert by_name["site-b"]["systemSnapshot"] is None
