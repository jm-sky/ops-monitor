"""Ops Monitor Agent.

Lightweight psutil-based agent that exposes system metrics via HTTP.
Deploy on each monitored server as a systemd service.

Endpoints:
  GET /health           - liveness probe (no auth)
  GET /system           - system metrics (Bearer token auth)
  GET /package-history  - apt install/upgrade/remove history (Bearer token auth)
"""

import gzip
import logging
import os
import re
import subprocess
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone, tzinfo
from pathlib import Path
from zoneinfo import ZoneInfo

import psutil
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import JSONResponse

load_dotenv()

AGENT_TOKEN: str = os.getenv("AGENT_TOKEN", "")
AGENT_HOST: str = os.getenv("AGENT_HOST", "0.0.0.0")
AGENT_PORT: int = int(os.getenv("AGENT_PORT", "9100"))
AGENT_VERSION: str = "1.3.0"
# IANA zone of the server clock. apt history.log timestamps carry no zone; when unset the
# agent process local zone is used (set this when running in Docker with TZ=UTC).
AGENT_APT_LOG_TZ: str = os.getenv("AGENT_APT_LOG_TZ", "")
# Override the directory holding history.log* (default: /host/var/log/apt, then /var/log/apt).
AGENT_APT_LOG_DIR: str = os.getenv("AGENT_APT_LOG_DIR", "")
# Directory holding reboot-required / reboot-required.pkgs. When set, only this directory is
# used (no fallback); when empty, the first existing of _REBOOT_DIR_CANDIDATES is used.
AGENT_REBOOT_FLAG_DIR: str = os.getenv("AGENT_REBOOT_FLAG_DIR", "")

logger = logging.getLogger("ops-monitor-agent")

# Cache update-check results for 5 minutes
_updates_cache: dict = {}
_UPDATES_CACHE_TTL = 300

# Cache parsed apt history for 5 minutes (parsing rotated .gz logs is the costly part)
_history_cache: dict = {}
_HISTORY_CACHE_TTL = 300


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    _get_reboot_info()  # log the reboot flag source (or why detection is off) at startup
    yield


app = FastAPI(
    title="Ops Monitor Agent", docs_url=None, redoc_url=None, lifespan=lifespan
)


# Hardened Docker mode mounts only a host-synced copy of the reboot flags at /host/reboot
# (see scripts/agent-host-sync-install.sh); /host/var/run is the legacy full /var/run mount.
_REBOOT_LEGACY_DIRS = [Path("/host/var/run"), Path("/var/run")]
_REBOOT_DIR_CANDIDATES = [Path("/host/reboot"), *_REBOOT_LEGACY_DIRS]
_REBOOT_FLAG_NAME = "reboot-required"
_REBOOT_PKGS_NAME = "reboot-required.pkgs"
# Touched by the host sync script on every run; proves the sync is installed and alive.
_REBOOT_SYNC_MARKER = ".last-sync"


# Prefer host-mounted /var/log/apt when running in Docker.
_APT_LOG_DIR_CANDIDATES = [
    Path("/host/var/log/apt"),
    Path("/var/log/apt"),
]


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


def verify_token(authorization: str | None) -> None:
    if not AGENT_TOKEN:
        return  # no token configured → open (dev mode)
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    if authorization[7:] != AGENT_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")


# ---------------------------------------------------------------------------
# System data helpers
# ---------------------------------------------------------------------------


def _reboot_dir_candidates() -> list[Path]:
    if AGENT_REBOOT_FLAG_DIR:
        return [Path(AGENT_REBOOT_FLAG_DIR)]
    return _REBOOT_DIR_CANDIDATES


def resolve_reboot_source(candidates: list[Path]) -> Path | None:
    """Return the first candidate that is an existing directory."""
    for path in candidates:
        if path.is_dir():
            return path
    return None


def _in_container() -> bool:
    return Path("/.dockerenv").exists()


def _reboot_source_problem(source: Path | None, synced_at: str | None) -> str | None:
    """Explain why reboot detection is unreliable for *source*, or None when it is fine."""
    if source is None:
        tried = ", ".join(str(p) for p in _reboot_dir_candidates())
        return f"no reboot flag directory found (tried: {tried}), reboot detection disabled"
    if source not in _REBOOT_LEGACY_DIRS and synced_at is None:
        return (
            f"{source} has no {_REBOOT_SYNC_MARKER} marker: host sync not installed "
            "(run scripts/agent-host-sync-install.sh on the host), reboot detection disabled"
        )
    if source == Path("/var/run") and _in_container():
        return "reading the container's own /var/run, not the host's /run; reboot detection disabled"
    return None


def read_reboot_info(source: Path | None) -> dict:
    """Detect reboot requirement (Debian/Ubuntu) from flag files in *source*."""
    info: dict = {
        "reboot_required": False,
        "reboot_reason": None,
        "reboot_detected_at": None,
        "reboot_source": str(source) if source is not None else None,
        "reboot_flags_synced_at": None,
    }
    if source is None:
        return info

    marker = source / _REBOOT_SYNC_MARKER
    if marker.is_file():
        info["reboot_flags_synced_at"] = datetime.fromtimestamp(
            marker.stat().st_mtime, tz=timezone.utc
        ).isoformat()

    flag = source / _REBOOT_FLAG_NAME
    if not flag.is_file():
        return info

    # The host sync copies with cp -p, so mtime is when the host raised the flag.
    info["reboot_required"] = True
    info["reboot_detected_at"] = datetime.fromtimestamp(
        flag.stat().st_mtime, tz=timezone.utc
    ).isoformat()

    reason = "kernel update"
    pkgs_file = source / _REBOOT_PKGS_NAME
    if pkgs_file.is_file():
        try:
            pkgs = pkgs_file.read_text().strip().splitlines()
            if pkgs:
                reason = ", ".join(pkgs[:5])
        except OSError:
            pass
    info["reboot_reason"] = reason
    return info


# Last reported reboot-source state, so problems are logged once per change, not per request.
_reboot_source_state: tuple[str | None, str | None] | None = None


def _log_reboot_source(source: Path | None, problem: str | None) -> None:
    global _reboot_source_state

    state = (str(source) if source is not None else None, problem)
    if state == _reboot_source_state:
        return
    _reboot_source_state = state
    if problem:
        logger.warning("Reboot flags: %s", problem)
    else:
        logger.info("Reboot flags: reading from %s", source)


def _get_reboot_info() -> dict:
    source = resolve_reboot_source(_reboot_dir_candidates())
    info = read_reboot_info(source)
    _log_reboot_source(
        source, _reboot_source_problem(source, info["reboot_flags_synced_at"])
    )
    return info


def _parse_no_cache(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in ("1", "true", "yes")


def _get_update_info(no_cache: bool = False) -> dict:
    """Detect available package updates (Debian/Ubuntu APT). Cached 5 min."""
    global _updates_cache

    now = time.monotonic()
    if (
        not no_cache
        and _updates_cache
        and now - _updates_cache.get("_ts", 0) < _UPDATES_CACHE_TTL
    ):
        return {k: v for k, v in _updates_cache.items() if not k.startswith("_")}

    updates_available = 0
    security_updates = 0
    security_packages: list[str] = []
    notifier_has_data = False

    try:
        if not no_cache:
            notifier = Path("/var/lib/update-notifier/updates-available")
        else:
            notifier = None
        if notifier is not None and notifier.exists():
            for line in notifier.read_text().splitlines():
                line = line.strip()
                if line and line[0].isdigit():
                    # Skip ESM/Pro lines — not immediately installable
                    if "esm" in line.lower() or "additional" in line.lower():
                        continue
                    count = int(line.split()[0])
                    if "security" in line.lower():
                        security_updates = count
                    else:
                        updates_available += count
                    notifier_has_data = True
    except Exception:
        pass

    if no_cache or not notifier_has_data:
        try:
            proc = subprocess.run(
                ["apt", "list", "--upgradable"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            all_packages: list[str] = []
            for line in proc.stdout.splitlines():
                if "/" not in line:
                    continue
                pkg = line.split("/")[0]
                all_packages.append(pkg)
                if "security" in line.lower():
                    security_packages.append(pkg)
            if all_packages:
                updates_available = len(all_packages) - len(security_packages)
                security_updates = len(security_packages)
        except Exception:
            pass

    result = {
        "updates_available": updates_available + security_updates,
        "security_updates": security_updates,
        "security_packages": security_packages,
        "system_state": (
            "up_to_date" if (updates_available + security_updates) == 0 else "outdated"
        ),
    }
    _updates_cache = {"_ts": now, **result}
    return result


def _apt_log_tz() -> tzinfo | None:
    if AGENT_APT_LOG_TZ:
        try:
            return ZoneInfo(AGENT_APT_LOG_TZ)
        except Exception:
            return None
    return None  # naive.astimezone() → process local zone


def _parse_apt_date(value: str | None) -> datetime | None:
    """Parse apt's ``2026-07-20  06:15:01`` (server local time) into an aware datetime."""
    if not value:
        return None
    try:
        naive = datetime.strptime(" ".join(value.split()), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    tz = _apt_log_tz()
    return naive.replace(tzinfo=tz) if tz else naive.astimezone()


_PKG_ENTRY = re.compile(r"(\S+?)\s+\(([^)]*)\)")
_PKG_ACTIONS = {"Install": "install", "Upgrade": "upgrade", "Remove": "remove", "Purge": "purge"}


def _parse_package_list(action: str, value: str) -> list[dict]:
    """Parse ``pkg:amd64 (1.0, automatic), other:all (1.0, 2.0)`` into package dicts."""
    packages: list[dict] = []
    for name_arch, inner in _PKG_ENTRY.findall(value):
        name, _, arch = name_arch.partition(":")
        versions = [part.strip() for part in inner.split(",")]
        auto_installed = "automatic" in versions[1:]
        versions = [v for v in versions if v != "automatic"]
        if action == "upgrade":
            from_version = versions[0] if versions else None
            to_version = versions[1] if len(versions) > 1 else None
        elif action == "install":
            from_version, to_version = None, (versions[0] if versions else None)
        else:  # remove / purge
            from_version, to_version = (versions[0] if versions else None), None
        packages.append(
            {
                "name": name,
                "arch": arch or None,
                "from_version": from_version,
                "to_version": to_version,
                "auto_installed": auto_installed,
            }
        )
    return packages


def parse_apt_history(text: str) -> list[dict]:
    """Parse the contents of an apt ``history.log`` into events (oldest first).

    A block is a run of ``Key: value`` lines separated by blank lines. Blocks without a valid
    Start-Date are skipped; a missing End-Date (interrupted run) yields ``finished_at=None``.
    An event is ``automatic`` when its Commandline mentions unattended-upgrade or there is no
    Requested-By (i.e. nobody invoked it through sudo/login).
    """
    events: list[dict] = []
    for raw_block in re.split(r"\n\s*\n", text):
        fields: dict[str, str] = {}
        for line in raw_block.splitlines():
            key, sep, value = line.partition(":")
            if sep and key.strip() and " " not in key.strip():
                fields[key.strip()] = value.strip()

        started_at = _parse_apt_date(fields.get("Start-Date"))
        if started_at is None:
            continue
        finished_at = _parse_apt_date(fields.get("End-Date"))
        commandline = fields.get("Commandline") or None
        requested_by = fields.get("Requested-By") or None

        packages = {
            target: _parse_package_list(target, fields[source])
            for source, target in _PKG_ACTIONS.items()
            if source in fields
        }
        events.append(
            {
                "started_at": started_at.isoformat(),
                "finished_at": finished_at.isoformat() if finished_at else None,
                "commandline": commandline,
                "requested_by": requested_by,
                "automatic": bool(
                    (commandline and "unattended-upgrade" in commandline) or not requested_by
                ),
                "packages": packages,
            }
        )
    events.sort(key=lambda e: datetime.fromisoformat(e["started_at"]))
    return events


def _apt_history_files() -> list[Path]:
    """history.log plus rotated history.log.N.gz from the first candidate dir that has any."""
    dirs = [Path(AGENT_APT_LOG_DIR)] if AGENT_APT_LOG_DIR else _APT_LOG_DIR_CANDIDATES
    for directory in dirs:
        try:
            files = [p for p in directory.glob("history.log*") if p.is_file() and re.fullmatch(r"history\.log(\.\d+(\.gz)?)?", p.name)]
        except OSError:
            continue
        if files:
            return sorted(files)
    return []


def _read_history_file(path: Path) -> str:
    try:
        if path.suffix == ".gz":
            with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
                return fh.read()
        return path.read_text(encoding="utf-8", errors="replace")
    except (OSError, EOFError, gzip.BadGzipFile):
        return ""


def _get_package_history(since: datetime | None = None, no_cache: bool = False) -> dict:
    """Return apt history events with started_at >= *since*. Parsed log is cached 5 min."""
    global _history_cache

    now = time.monotonic()
    if not no_cache and _history_cache and now - _history_cache.get("_ts", 0) < _HISTORY_CACHE_TTL:
        events: list[dict] = _history_cache["events"]
        sources: list[str] = _history_cache["sources"]
    else:
        files = _apt_history_files()
        by_start: dict[str, dict] = {}
        for path in files:
            for event in parse_apt_history(_read_history_file(path)):
                by_start[event["started_at"]] = event
        events = sorted(by_start.values(), key=lambda e: datetime.fromisoformat(e["started_at"]))
        sources = [str(p) for p in files]
        _history_cache = {"_ts": now, "events": events, "sources": sources}

    if since is not None:
        events = [e for e in events if datetime.fromisoformat(e["started_at"]) >= since]
    return {
        "events": events,
        "sources": sources,
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
    }


def _parse_since(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.strip())
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid 'since' (expected ISO 8601)") from None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _collect_system_metrics(no_cache: bool = False) -> dict:
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    try:
        load_avg = list(os.getloadavg())
    except (AttributeError, OSError):
        load_avg = [0.0, 0.0, 0.0]

    uptime_seconds = int(time.time() - psutil.boot_time())

    data: dict = {
        "version": AGENT_VERSION,
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "memory": {
            "total_mb": round(mem.total / 1024 / 1024, 1),
            "used_mb": round(mem.used / 1024 / 1024, 1),
            "percent": mem.percent,
        },
        "disk": {
            "total_gb": round(disk.total / 1024 / 1024 / 1024, 1),
            "used_gb": round(disk.used / 1024 / 1024 / 1024, 1),
            "percent": disk.percent,
        },
        "load_avg": [round(x, 2) for x in load_avg],
        "uptime_seconds": uptime_seconds,
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }

    data.update(_get_reboot_info())
    data.update(_get_update_info(no_cache=no_cache))
    return data


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/system")
async def system(
    authorization: str | None = Header(default=None),
    no_cache: str | None = Query(default=None),
) -> JSONResponse:
    verify_token(authorization)
    return JSONResponse(_collect_system_metrics(no_cache=_parse_no_cache(no_cache)))


@app.get("/package-history")
async def package_history(
    authorization: str | None = Header(default=None),
    since: str | None = Query(default=None),
    no_cache: str | None = Query(default=None),
) -> JSONResponse:
    verify_token(authorization)
    return JSONResponse(
        _get_package_history(
            since=_parse_since(since), no_cache=_parse_no_cache(no_cache)
        )
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(name)s - %(message)s")
    uvicorn.run(app, host=AGENT_HOST, port=AGENT_PORT, log_level="info")
