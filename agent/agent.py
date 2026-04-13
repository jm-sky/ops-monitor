"""Ops Monitor Agent.

Lightweight psutil-based agent that exposes system metrics via HTTP.
Deploy on each monitored server as a systemd service.

Endpoints:
  GET /health  - liveness probe (no auth)
  GET /system  - system metrics (Bearer token auth)
"""

import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse

load_dotenv()

AGENT_TOKEN: str = os.getenv("AGENT_TOKEN", "")
AGENT_HOST: str = os.getenv("AGENT_HOST", "0.0.0.0")
AGENT_PORT: int = int(os.getenv("AGENT_PORT", "9100"))

# Cache update-check results for 5 minutes
_updates_cache: dict = {}
_UPDATES_CACHE_TTL = 300

app = FastAPI(title="Ops Monitor Agent", docs_url=None, redoc_url=None)


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
    flag = Path("/var/run/reboot-required")
    if not flag.exists():
        return {"reboot_required": False, "reboot_reason": None, "reboot_detected_at": None}

    detected_at = datetime.fromtimestamp(flag.stat().st_mtime, tz=timezone.utc).isoformat()

    reason: str | None = None
    pkgs_file = Path("/var/run/reboot-required.pkgs")
    if pkgs_file.exists():
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


def _get_update_info() -> dict:
    """Detect available package updates (Debian/Ubuntu APT). Cached 5 min."""
    global _updates_cache

    now = time.monotonic()
    if _updates_cache and now - _updates_cache.get("_ts", 0) < _UPDATES_CACHE_TTL:
        return {k: v for k, v in _updates_cache.items() if not k.startswith("_")}

    updates_available = 0
    security_updates = 0
    security_packages: list[str] = []

    try:
        notifier = Path("/var/lib/update-notifier/updates-available")
        if notifier.exists():
            for line in notifier.read_text().splitlines():
                line = line.strip()
                if line and line[0].isdigit():
                    count = int(line.split()[0])
                    if "security" in line.lower():
                        security_updates = count
                    else:
                        updates_available += count
    except Exception:
        pass

    try:
        proc = subprocess.run(
            ["apt", "list", "--upgradable"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        for line in proc.stdout.splitlines():
            if "/" in line and "security" in line.lower():
                security_packages.append(line.split("/")[0])
        if security_packages:
            security_updates = len(security_packages)
    except Exception:
        pass

    result = {
        "updates_available": updates_available + security_updates,
        "security_updates": security_updates,
        "security_packages": security_packages,
        "system_state": "up_to_date" if (updates_available + security_updates) == 0 else "outdated",
    }
    _updates_cache = {"_ts": now, **result}
    return result


def _collect_system_metrics() -> dict:
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    try:
        load_avg = list(os.getloadavg())
    except (AttributeError, OSError):
        load_avg = [0.0, 0.0, 0.0]

    uptime_seconds = int(time.time() - psutil.boot_time())

    data: dict = {
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
    data.update(_get_update_info())
    return data


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/system")
async def system(authorization: str | None = Header(default=None)) -> JSONResponse:
    verify_token(authorization)
    return JSONResponse(_collect_system_metrics())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(app, host=AGENT_HOST, port=AGENT_PORT, log_level="info")
