"""Unit tests for monitor polling service."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.modules.monitor.db_models import SiteDB, SiteSnapshotDB
from app.modules.monitor.service import MonitorService, _append_query_param


def test_append_query_param_adds_to_bare_url() -> None:
    assert _append_query_param("http://host/system", "no_cache", "1") == (
        "http://host/system?no_cache=1"
    )


def test_append_query_param_merges_existing_query() -> None:
    merged = _append_query_param("http://host/system?foo=bar", "no_cache", "1")
    assert "foo=bar" in merged
    assert "no_cache=1" in merged


@pytest.mark.asyncio
async def test_poll_site_now_system_requests_no_cache() -> None:
    site = SiteDB(
        id=uuid.uuid4(),
        name="test",
        system_url="http://agent.example:9100/system",
        verify_ssl=True,
    )
    captured_urls: list[str] = []

    class FakeResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict:
            return {
                "reboot_required": False,
                "system_state": "up_to_date",
            }

    class FakeClient:
        async def get(self, url: str, headers: dict) -> FakeResponse:
            captured_urls.append(url)
            return FakeResponse()

        async def __aenter__(self) -> "FakeClient":
            return self

        async def __aexit__(self, *args: object) -> None:
            pass

    snap = SiteSnapshotDB(
        id=uuid.uuid4(),
        site_id=site.id,
        snapshot_type="system",
        status="up_to_date",
        raw_data={},
        polled_at=datetime.now(UTC),
    )

    mock_repo = MagicMock()
    mock_repo.create = AsyncMock(return_value=snap)
    mock_repo.cleanup_old = AsyncMock()

    mock_db = MagicMock()
    session_cm = AsyncMock()
    session_cm.__aenter__.return_value = mock_db
    session_cm.__aexit__.return_value = None

    with (
        patch("app.modules.monitor.service.httpx.AsyncClient", return_value=FakeClient()),
        patch("app.modules.monitor.service.AsyncSessionLocal", return_value=session_cm),
        patch("app.modules.monitor.service.SnapshotRepository", return_value=mock_repo),
        patch("app.modules.monitor.service.dispatch_if_changed", new_callable=AsyncMock),
    ):
        service = MonitorService()
        await service.poll_site_now(site)

    assert len(captured_urls) == 1
    assert "no_cache=1" in captured_urls[0]


@pytest.mark.asyncio
async def test_poll_due_sites_system_without_no_cache() -> None:
    site = SiteDB(
        id=uuid.uuid4(),
        name="test",
        enabled=True,
        system_url="http://agent.example:9100/system",
        polling_system=300,
        verify_ssl=True,
    )

    with (
        patch(
            "app.modules.monitor.service.SiteRepository",
        ) as mock_site_repo_cls,
        patch.object(MonitorService, "_poll_system", new_callable=AsyncMock) as mock_poll_system,
    ):
        mock_site_repo = MagicMock()
        mock_site_repo.get_enabled = AsyncMock(return_value=[site])
        mock_site_repo_cls.return_value = mock_site_repo

        session_cm = AsyncMock()
        session_cm.__aenter__.return_value = MagicMock()
        session_cm.__aexit__.return_value = None

        with patch("app.modules.monitor.service.AsyncSessionLocal", return_value=session_cm):
            service = MonitorService()
            await service.poll_due_sites({})

    mock_poll_system.assert_awaited_once_with(site)
