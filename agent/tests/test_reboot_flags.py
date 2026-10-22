"""Tests for reboot flag source selection, flag parsing and the host sync script."""

import logging
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

import agent

SYNC_SCRIPT = (
    Path(__file__).resolve().parents[2] / "scripts" / "lib" / "sync-reboot-flags.sh"
)

FLAG_MTIME = datetime(2026, 10, 20, 6, 15, tzinfo=timezone.utc).timestamp()


def _write_flag(directory: Path, pkgs: str | None = None) -> None:
    flag = directory / "reboot-required"
    flag.write_text("*** System restart required ***\n")
    os.utime(flag, (FLAG_MTIME, FLAG_MTIME))
    if pkgs is not None:
        (directory / "reboot-required.pkgs").write_text(pkgs)


@pytest.fixture(autouse=True)
def _reset_state(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(agent, "AGENT_REBOOT_FLAG_DIR", "")
    monkeypatch.setattr(agent, "_reboot_source_state", None)


@pytest.fixture
def dirs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Path]:
    """Point the candidate chain at tmp dirs (none created yet)."""
    sync = tmp_path / "host-reboot"
    legacy = tmp_path / "host-var-run"
    local = tmp_path / "var-run"
    monkeypatch.setattr(agent, "_REBOOT_LEGACY_DIRS", [legacy, local])
    monkeypatch.setattr(agent, "_REBOOT_DIR_CANDIDATES", [sync, legacy, local])
    return {"sync": sync, "legacy": legacy, "local": local}


# ---------------------------------------------------------------------------
# Source selection
# ---------------------------------------------------------------------------


def test_prefers_sync_dir(dirs: dict[str, Path]) -> None:
    for path in dirs.values():
        path.mkdir()
    assert agent.resolve_reboot_source(agent._reboot_dir_candidates()) == dirs["sync"]


def test_falls_back_to_legacy_when_sync_dir_missing(dirs: dict[str, Path]) -> None:
    dirs["legacy"].mkdir()
    dirs["local"].mkdir()
    assert agent.resolve_reboot_source(agent._reboot_dir_candidates()) == dirs["legacy"]


def test_no_candidate_exists(dirs: dict[str, Path]) -> None:
    info = agent._get_reboot_info()
    assert info["reboot_required"] is False
    assert info["reboot_source"] is None


def test_file_in_place_of_dir_is_skipped(dirs: dict[str, Path]) -> None:
    dirs["sync"].write_text("")  # not a directory
    dirs["legacy"].mkdir()
    assert agent.resolve_reboot_source(agent._reboot_dir_candidates()) == dirs["legacy"]


def test_explicit_dir_has_no_fallback(
    dirs: dict[str, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    dirs["legacy"].mkdir()
    _write_flag(dirs["legacy"])
    monkeypatch.setattr(agent, "AGENT_REBOOT_FLAG_DIR", str(tmp_path / "missing"))

    info = agent._get_reboot_info()
    assert info["reboot_source"] is None
    assert info["reboot_required"] is False


def test_explicit_dir_is_used(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    custom = tmp_path / "custom"
    custom.mkdir()
    _write_flag(custom)
    monkeypatch.setattr(agent, "AGENT_REBOOT_FLAG_DIR", str(custom))

    info = agent._get_reboot_info()
    assert info["reboot_source"] == str(custom)
    assert info["reboot_required"] is True


# ---------------------------------------------------------------------------
# Flag parsing
# ---------------------------------------------------------------------------


def test_flag_with_pkgs(tmp_path: Path) -> None:
    _write_flag(tmp_path, "linux-image-6.8.0-107-generic\nlinux-base\n")
    info = agent.read_reboot_info(tmp_path)
    assert info["reboot_required"] is True
    assert info["reboot_reason"] == "linux-image-6.8.0-107-generic, linux-base"
    assert (
        info["reboot_detected_at"]
        == datetime.fromtimestamp(FLAG_MTIME, tz=timezone.utc).isoformat()
    )
    assert info["reboot_source"] == str(tmp_path)


def test_flag_without_pkgs(tmp_path: Path) -> None:
    _write_flag(tmp_path)
    assert agent.read_reboot_info(tmp_path)["reboot_reason"] == "kernel update"


def test_empty_pkgs_file(tmp_path: Path) -> None:
    _write_flag(tmp_path, "")
    assert agent.read_reboot_info(tmp_path)["reboot_reason"] == "kernel update"


def test_pkgs_limited_to_five(tmp_path: Path) -> None:
    _write_flag(tmp_path, "\n".join(f"pkg{i}" for i in range(8)))
    assert (
        agent.read_reboot_info(tmp_path)["reboot_reason"]
        == "pkg0, pkg1, pkg2, pkg3, pkg4"
    )


def test_no_flag(tmp_path: Path) -> None:
    (tmp_path / "reboot-required.pkgs").write_text(
        "linux-base\n"
    )  # orphan .pkgs is ignored
    info = agent.read_reboot_info(tmp_path)
    assert info["reboot_required"] is False
    assert info["reboot_reason"] is None
    assert info["reboot_detected_at"] is None


def test_flag_that_is_a_directory_is_ignored(tmp_path: Path) -> None:
    (
        tmp_path / "reboot-required"
    ).mkdir()  # left behind by the old single-file bind mount
    assert agent.read_reboot_info(tmp_path)["reboot_required"] is False


def test_does_not_mix_sources(dirs: dict[str, Path]) -> None:
    dirs["sync"].mkdir()
    dirs["legacy"].mkdir()
    _write_flag(
        dirs["legacy"], "linux-base\n"
    )  # only the lower-priority dir has a flag
    assert agent._get_reboot_info()["reboot_required"] is False


# ---------------------------------------------------------------------------
# Sync marker and diagnostics
# ---------------------------------------------------------------------------


def test_synced_at_from_marker(tmp_path: Path) -> None:
    marker = tmp_path / ".last-sync"
    marker.touch()
    os.utime(marker, (FLAG_MTIME, FLAG_MTIME))
    info = agent.read_reboot_info(tmp_path)
    assert (
        info["reboot_flags_synced_at"]
        == datetime.fromtimestamp(FLAG_MTIME, tz=timezone.utc).isoformat()
    )


def test_warns_when_sync_marker_missing(
    dirs: dict[str, Path], caplog: pytest.LogCaptureFixture
) -> None:
    dirs["sync"].mkdir()
    with caplog.at_level(logging.INFO, logger="ops-monitor-agent"):
        agent._get_reboot_info()
    assert any(
        r.levelno == logging.WARNING and "host sync not installed" in r.getMessage()
        for r in caplog.records
    )


def test_info_when_sync_marker_present(
    dirs: dict[str, Path], caplog: pytest.LogCaptureFixture
) -> None:
    dirs["sync"].mkdir()
    (dirs["sync"] / ".last-sync").touch()
    with caplog.at_level(logging.INFO, logger="ops-monitor-agent"):
        agent._get_reboot_info()
    assert [r.levelno for r in caplog.records] == [logging.INFO]
    assert str(dirs["sync"]) in caplog.records[0].getMessage()


def test_legacy_dir_needs_no_marker(
    dirs: dict[str, Path], caplog: pytest.LogCaptureFixture
) -> None:
    dirs["legacy"].mkdir()
    with caplog.at_level(logging.INFO, logger="ops-monitor-agent"):
        agent._get_reboot_info()
    assert not any(r.levelno >= logging.WARNING for r in caplog.records)


def test_warns_when_no_source(
    dirs: dict[str, Path], caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO, logger="ops-monitor-agent"):
        agent._get_reboot_info()
    assert "reboot detection disabled" in caplog.records[0].getMessage()


def test_warning_logged_once_per_state(
    dirs: dict[str, Path], caplog: pytest.LogCaptureFixture
) -> None:
    dirs["sync"].mkdir()
    with caplog.at_level(logging.INFO, logger="ops-monitor-agent"):
        agent._get_reboot_info()
        agent._get_reboot_info()
        (dirs["sync"] / ".last-sync").touch()  # sync installed later → state changes
        agent._get_reboot_info()
    assert [r.levelno for r in caplog.records] == [logging.WARNING, logging.INFO]


def test_system_endpoint_reports_source(
    dirs: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    from fastapi.testclient import TestClient

    dirs["sync"].mkdir()
    (dirs["sync"] / ".last-sync").touch()
    _write_flag(dirs["sync"])
    monkeypatch.setattr(agent, "AGENT_TOKEN", "")
    monkeypatch.setattr(
        agent, "_updates_cache", {"_ts": 1e18, "system_state": "up_to_date"}
    )

    data = TestClient(agent.app).get("/system").json()
    assert data["reboot_required"] is True
    assert data["reboot_source"] == str(dirs["sync"])
    assert data["reboot_flags_synced_at"] is not None


# ---------------------------------------------------------------------------
# Host sync script (scripts/lib/sync-reboot-flags.sh)
# ---------------------------------------------------------------------------


def _run_sync(src: Path, dest: Path) -> None:
    subprocess.run(
        ["bash", str(SYNC_SCRIPT)],
        env={
            **os.environ,
            "OPS_AGENT_REBOOT_SRC": str(src),
            "OPS_AGENT_REBOOT_DEST": str(dest),
        },
        check=True,
    )


def test_sync_copies_flags_with_mtime(tmp_path: Path) -> None:
    src, dest = tmp_path / "run", tmp_path / "copy"
    src.mkdir()
    _write_flag(src, "linux-base\n")

    _run_sync(src, dest)

    assert (dest / "reboot-required").stat().st_mtime == FLAG_MTIME
    assert (dest / "reboot-required.pkgs").read_text() == "linux-base\n"
    assert (dest / ".last-sync").is_file()
    assert agent.read_reboot_info(dest)["reboot_required"] is True
    assert sorted(p.name for p in dest.iterdir()) == [
        ".last-sync",
        "reboot-required",
        "reboot-required.pkgs",
    ]


def test_sync_removes_copies_when_originals_gone(tmp_path: Path) -> None:
    src, dest = tmp_path / "run", tmp_path / "copy"
    src.mkdir()
    _write_flag(src, "linux-base\n")
    _run_sync(src, dest)

    (src / "reboot-required").unlink()
    (src / "reboot-required.pkgs").unlink()
    _run_sync(src, dest)

    assert sorted(p.name for p in dest.iterdir()) == [".last-sync"]
    assert agent.read_reboot_info(dest)["reboot_required"] is False


def test_sync_ignores_directory_in_place_of_flag(tmp_path: Path) -> None:
    src, dest = tmp_path / "run", tmp_path / "copy"
    (src / "reboot-required").mkdir(parents=True)

    _run_sync(src, dest)

    assert not (dest / "reboot-required").exists()
    assert (dest / ".last-sync").is_file()


def test_sync_is_idempotent(tmp_path: Path) -> None:
    src, dest = tmp_path / "run", tmp_path / "copy"
    src.mkdir()
    _write_flag(src)
    _run_sync(src, dest)
    _run_sync(src, dest)
    assert sorted(p.name for p in dest.iterdir()) == [".last-sync", "reboot-required"]
