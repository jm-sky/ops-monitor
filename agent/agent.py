"""Ops Monitor Agent.

Lightweight psutil-based agent that exposes system metrics via HTTP.
Deploy on each monitored server as a systemd service.

Endpoints:
  GET /health           - liveness probe (no auth)
  GET /system           - system metrics (Bearer token auth)
  GET /package-history  - apt install/upgrade/remove history (Bearer token auth)
"""

import gzip
import os
import re
import subprocess
import time
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
AGENT_VERSION: str = "1.2.0"
# IANA zone of the server clock. apt history.log timestamps carry no zone; when unset the
# agent process local zone is used (set this when running in Docker with TZ=UTC).
AGENT_APT_LOG_TZ: str = os.getenv("AGENT_APT_LOG_TZ", "")
# Override the directory holding history.log* (default: /host/var/log/apt, then /var/log/apt).
AGENT_APT_LOG_DIR: str = os.getenv("AGENT_APT_LOG_DIR", "")

# Cache update-check results for 5 minutes
_updates_cache: dict = {}
_UPDATES_CACHE_TTL = 300

# Cache parsed apt history for 5 minutes (parsing rotated .gz logs is the costly part)
_history_cache: dict = {}
_HISTORY_CACHE_TTL = 300

app = FastAPI(title="Ops Monitor Agent", docs_url=None, redoc_url=None)


# Prefer host-mounted /var/run when running in Docker.
_REBOOT_FLAG_CANDIDATES = [
    Path("/host/var/run/reboot-required"),
    Path("/var/run/reboot-required"),
]
_REBOOT_PKGS_CANDIDATES = [
    Path("/host/var/run/reboot-required.pkgs"),
    Path("/var/run/reboot-required.pkgs"),
]


# Prefer host-mounted /var/log/apt when running in Docker.
_APT_LOG_DIR_CANDIDATES = [
    Path("/host/var/log/apt"),
    Path("/var/log/apt"),
]


def _first_existing_file(candidates: list[Path]) -> Path | None:
    for path in candidates:
        if path.is_file():
            return path
    return None


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


def _get_reboot_info() -> dict:
    """Detect reboot requirement (Debian/Ubuntu)."""
    flag = _first_existing_file(_REBOOT_FLAG_CANDIDATES)
    if flag is None:
        return {
            "reboot_required": False,
            "reboot_reason": None,
            "reboot_detected_at": None,
        }

    detected_at = datetime.fromtimestamp(
        flag.stat().st_mtime, tz=timezone.utc
    ).isoformat()

    reason: str | None = None
    pkgs_file = _first_existing_file(_REBOOT_PKGS_CANDIDATES)
    if pkgs_file is not None:
        try:
            pkgs = pkgs_file.read_text().strip().splitlines()
            reason = ", ".join(pkgs[:5]) if pkgs else "kernel update"
        except OSError:
            reason = "kernel update"
    else:
        reason = "kernel update"

    return {
        "reboot_required": True,
        "reboot_reason": reason,
        "reboot_detected_at": detected_at,
    }


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
    uvicorn.run(app, host=AGENT_HOST, port=AGENT_PORT, log_level="info")
