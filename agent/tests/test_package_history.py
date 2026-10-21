"""Tests for apt history.log parsing and the /package-history endpoint."""

import gzip
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import agent

HISTORY_LOG = """\
Start-Date: 2026-07-01  09:00:00
Commandline: apt install htop
Requested-By: jan (1000)
Install: htop:amd64 (3.3.0-1), libnl-3-200:amd64 (3.7.0-0.3, automatic)
End-Date: 2026-07-01  09:00:10

Start-Date: 2026-07-02  06:15:01
Commandline: /usr/bin/unattended-upgrade
Upgrade: openssl:amd64 (3.0.13-1, 3.0.13-2), libssl3:amd64 (3.0.13-1, 3.0.13-2)
End-Date: 2026-07-02  06:15:40

Start-Date: 2026-07-03  10:00:00
Commandline: apt-get remove --purge nano
Requested-By: jan (1000)
Remove: nano:amd64 (7.2-1)
Purge: nano-doc:all (7.2-1)
End-Date: 2026-07-03  10:00:05

Start-Date: 2026-07-04  11:00:00
Commandline: apt upgrade
Requested-By: jan (1000)
Upgrade: curl:amd64 (8.5.0-1, 8.5.0-2)
"""

ROTATED_LOG = """\
Start-Date: 2026-06-01  08:00:00
Commandline: apt upgrade
Requested-By: anna (1001)
Upgrade: git:amd64 (1:2.43.0-1, 1:2.43.0-2)
End-Date: 2026-06-01  08:01:00
"""


@pytest.fixture(autouse=True)
def _utc_logs(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setattr(agent, "AGENT_APT_LOG_TZ", "UTC")
    monkeypatch.setattr(agent, "AGENT_TOKEN", "secret")
    agent._history_cache.clear()
    yield
    agent._history_cache.clear()


@pytest.fixture
def log_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / "history.log").write_text(HISTORY_LOG)
    with gzip.open(tmp_path / "history.log.1.gz", "wt") as fh:
        fh.write(ROTATED_LOG)
    (tmp_path / "term.log").write_text("not a history file")
    monkeypatch.setattr(agent, "AGENT_APT_LOG_DIR", str(tmp_path))
    return tmp_path


def test_parses_multiple_blocks() -> None:
    events = agent.parse_apt_history(HISTORY_LOG)

    assert [e["started_at"] for e in events] == [
        "2026-07-01T09:00:00+00:00",
        "2026-07-02T06:15:01+00:00",
        "2026-07-03T10:00:00+00:00",
        "2026-07-04T11:00:00+00:00",
    ]
    install = events[0]
    assert install["finished_at"] == "2026-07-01T09:00:10+00:00"
    assert install["commandline"] == "apt install htop"
    assert install["requested_by"] == "jan (1000)"
    assert install["packages"]["install"] == [
        {"name": "htop", "arch": "amd64", "from_version": None, "to_version": "3.3.0-1", "auto_installed": False},
        {"name": "libnl-3-200", "arch": "amd64", "from_version": None, "to_version": "3.7.0-0.3", "auto_installed": True},
    ]


def test_parses_upgrade_remove_and_purge_versions() -> None:
    events = agent.parse_apt_history(HISTORY_LOG)

    upgrade = events[1]["packages"]["upgrade"][0]
    assert (upgrade["name"], upgrade["from_version"], upgrade["to_version"]) == ("openssl", "3.0.13-1", "3.0.13-2")
    removed = events[2]["packages"]
    assert removed["remove"][0]["from_version"] == "7.2-1"
    assert removed["remove"][0]["to_version"] is None
    assert removed["purge"][0]["name"] == "nano-doc"
    assert removed["purge"][0]["arch"] == "all"


def test_epoch_versions_are_kept() -> None:
    event = agent.parse_apt_history(ROTATED_LOG)[0]
    assert event["packages"]["upgrade"][0]["from_version"] == "1:2.43.0-1"


def test_missing_end_date_gives_null_finished_at() -> None:
    last = agent.parse_apt_history(HISTORY_LOG)[-1]
    assert last["started_at"] == "2026-07-04T11:00:00+00:00"
    assert last["finished_at"] is None


def test_unattended_upgrade_is_automatic() -> None:
    events = agent.parse_apt_history(HISTORY_LOG)
    assert events[1]["automatic"] is True
    assert events[1]["requested_by"] is None


def test_missing_requested_by_is_automatic_even_without_unattended() -> None:
    text = "Start-Date: 2026-07-05  01:00:00\nCommandline: apt-get -y upgrade\nUpgrade: a:amd64 (1, 2)\nEnd-Date: 2026-07-05  01:00:05\n"
    assert agent.parse_apt_history(text)[0]["automatic"] is True


def test_user_run_with_requested_by_is_not_automatic() -> None:
    events = agent.parse_apt_history(HISTORY_LOG)
    assert [e["automatic"] for e in events] == [False, True, False, False]


def test_blocks_without_valid_start_date_are_skipped() -> None:
    text = "Commandline: apt update\n\nStart-Date: garbage\nCommandline: x\n\n" + ROTATED_LOG
    assert len(agent.parse_apt_history(text)) == 1


def test_naive_dates_use_configured_timezone(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(agent, "AGENT_APT_LOG_TZ", "Europe/Warsaw")
    event = agent.parse_apt_history(ROTATED_LOG)[0]
    assert event["started_at"] == "2026-06-01T08:00:00+02:00"


def test_reads_plain_and_gzipped_files_sorted(log_dir: Path) -> None:
    result = agent._get_package_history()

    starts = [e["started_at"] for e in result["events"]]
    assert starts[0] == "2026-06-01T08:00:00+00:00"
    assert len(starts) == 5
    assert sorted(p.rsplit("/", 1)[-1] for p in result["sources"]) == ["history.log", "history.log.1.gz"]


def test_since_filters_events_inclusive(log_dir: Path) -> None:
    since = datetime(2026, 7, 3, 10, 0, 0, tzinfo=timezone.utc)
    result = agent._get_package_history(since=since)
    assert [e["started_at"] for e in result["events"]] == [
        "2026-07-03T10:00:00+00:00",
        "2026-07-04T11:00:00+00:00",
    ]


def test_corrupt_gz_is_ignored(log_dir: Path) -> None:
    (log_dir / "history.log.2.gz").write_bytes(b"not gzip")
    assert len(agent._get_package_history()["events"]) == 5


def test_no_log_files_returns_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(agent, "AGENT_APT_LOG_DIR", str(tmp_path))
    assert agent._get_package_history()["events"] == []


def test_result_is_cached_until_no_cache(log_dir: Path) -> None:
    assert len(agent._get_package_history()["events"]) == 5
    (log_dir / "history.log").write_text("")
    assert len(agent._get_package_history()["events"]) == 5
    assert len(agent._get_package_history(no_cache=True)["events"]) == 1


# --- endpoint ---------------------------------------------------------------


@pytest.fixture
def client() -> TestClient:
    return TestClient(agent.app)


def test_endpoint_requires_token(client: TestClient, log_dir: Path) -> None:
    assert client.get("/package-history").status_code == 401
    assert client.get("/package-history", headers={"Authorization": "Bearer wrong"}).status_code == 403


def test_endpoint_returns_events_and_honours_since(client: TestClient, log_dir: Path) -> None:
    headers = {"Authorization": "Bearer secret"}

    all_events = client.get("/package-history", headers=headers).json()["events"]
    assert len(all_events) == 5

    response = client.get("/package-history", params={"since": "2026-07-04T00:00:00Z"}, headers=headers)
    assert response.status_code == 200
    assert [e["started_at"] for e in response.json()["events"]] == ["2026-07-04T11:00:00+00:00"]


def test_endpoint_rejects_invalid_since(client: TestClient, log_dir: Path) -> None:
    response = client.get("/package-history", params={"since": "yesterday"}, headers={"Authorization": "Bearer secret"})
    assert response.status_code == 422
