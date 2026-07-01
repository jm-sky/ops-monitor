"""Monitor management CLI commands."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import typer
from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from app.modules.monitor.db_models import SiteDB, SiteSnapshotDB

RowStyle = Literal["red", "yellow", "green", "dim"]
RowKind = Literal["error", "warn", "ok", "neutral"]

_ERR_COL_MAX = 72


def _format_error_cell(
    health_snap: SiteSnapshotDB | None,
    system_snap: SiteSnapshotDB | None,
    ssl_snap: SiteSnapshotDB | None = None,
) -> str:
    parts: list[str] = []
    if health_snap and health_snap.error and health_snap.error.strip():
        parts.append(f"health: {health_snap.error.strip()}")
    if system_snap and system_snap.error and system_snap.error.strip():
        parts.append(f"system: {system_snap.error.strip()}")
    if ssl_snap and ssl_snap.error and ssl_snap.error.strip():
        parts.append(f"cert: {ssl_snap.error.strip()}")
    text = "; ".join(parts) if parts else "—"
    if len(text) > _ERR_COL_MAX:
        return text[: _ERR_COL_MAX - 1] + "…"
    return text


def _format_last_poll(
    health_snap: SiteSnapshotDB | None,
    system_snap: SiteSnapshotDB | None,
    ssl_snap: SiteSnapshotDB | None = None,
) -> str:
    times: list[datetime] = []
    if health_snap:
        times.append(health_snap.polled_at)
    if system_snap:
        times.append(system_snap.polled_at)
    if ssl_snap:
        times.append(ssl_snap.polled_at)
    if not times:
        return "—"
    latest = max(times)
    latest_utc = latest.astimezone(UTC) if latest.tzinfo else latest.replace(tzinfo=UTC)
    return latest_utc.strftime("%Y-%m-%d %H:%M UTC")


def _status_display(snap: SiteSnapshotDB | None) -> str:
    if snap is None:
        return "—"
    if not snap.status:
        return "—"
    return snap.status


def _cert_display(snap: SiteSnapshotDB | None) -> str:
    if snap is None:
        return "—"
    if snap.status == "expired":
        return "EXPIRED"
    if snap.status == "failed":
        return "ERROR"
    days = (snap.raw_data or {}).get("days_remaining")
    if isinstance(days, int):
        return f"{days}d"
    return snap.status or "—"


def _row_style_and_kind(
    site: SiteDB,
    health_snap: SiteSnapshotDB | None,
    system_snap: SiteSnapshotDB | None,
    ssl_snap: SiteSnapshotDB | None = None,
) -> tuple[RowStyle, RowKind]:
    """Classify row for Rich styling and --errors-only filtering.

    - red: any snapshot error text, or status failed on health/system, or cert
      failed/expired.
    - yellow: health degraded; system reboot_required/outdated; cert
      expiring_soon; missing snapshot when the corresponding URL is
      configured (never polled yet).
    - dim: no health_url/system_url/ssl_check_url — nothing to evaluate (not
      "all OK").
    - green: expected snapshots present with OK health + up_to_date system +
      ok cert.
    """
    has_h = bool(site.health_url)
    has_s = bool(site.system_url)
    has_c = bool(site.ssl_check_url)

    h_err = (health_snap.error or "").strip() if has_h and health_snap else ""
    s_err = (system_snap.error or "").strip() if has_s and system_snap else ""
    c_err = (ssl_snap.error or "").strip() if has_c and ssl_snap else ""
    h_stat = health_snap.status if has_h and health_snap else None
    s_stat = system_snap.status if has_s and system_snap else None
    c_stat = ssl_snap.status if has_c and ssl_snap else None

    if h_err or s_err or c_err:
        return "red", "error"
    if h_stat == "failed" or s_stat == "failed" or c_stat in ("failed", "expired"):
        return "red", "error"

    if h_stat == "degraded":
        return "yellow", "warn"
    if s_stat in ("reboot_required", "outdated"):
        return "yellow", "warn"
    if c_stat == "expiring_soon":
        return "yellow", "warn"
    if has_h and health_snap is None:
        return "yellow", "warn"
    if has_s and system_snap is None:
        return "yellow", "warn"
    if has_c and ssl_snap is None:
        return "yellow", "warn"

    if not has_h and not has_s and not has_c:
        return "dim", "neutral"

    if has_h and health_snap is not None and h_stat != "ok":
        return "yellow", "warn"
    if has_s and system_snap is not None and s_stat != "up_to_date":
        return "yellow", "warn"
    if has_c and ssl_snap is not None and c_stat != "ok":
        return "yellow", "warn"

    return "green", "ok"


def _include_in_errors_only(kind: RowKind) -> bool:
    return kind in ("error", "warn")


monitor_app = typer.Typer(
    name="monitor",
    help="Monitor module management",
    no_args_is_help=True,
)

console = Console()


@monitor_app.command("seed-sites")
def seed_sites(
    yaml_file: Path = typer.Argument(
        Path("seeds/sites.yml"),
        help="Path to YAML seed file (relative to /app)",
    ),
    dry_run: bool | None = typer.Option(
        None,
        "--dry-run/--no-dry-run",
        help="Show what would be imported without saving",
    ),
    clear: bool | None = typer.Option(
        None, "--clear/--no-clear", help="Delete all existing sites before seeding"
    ),
) -> None:
    """Seed sites from a YAML file (upsert by name)."""
    if dry_run is None:
        dry_run = typer.confirm("Dry run (no changes saved)?", default=False)
    if clear is None:
        clear = typer.confirm("Clear all existing sites before seeding?", default=False)
    asyncio.run(_seed_sites(yaml_file, dry_run, clear))


async def _seed_sites(yaml_file: Path, dry_run: bool, clear: bool) -> None:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        console.print("[red]PyYAML not installed. Run: pip install pyyaml[/red]")
        raise typer.Exit(1)

    if not yaml_file.exists():
        console.print(f"[red]File not found: {yaml_file}[/red]")
        raise typer.Exit(1)

    data = yaml.safe_load(yaml_file.read_text())
    # Support both root list and {sites: [...]} format
    sites = data if isinstance(data, list) else data.get("sites", [])

    if not sites:
        console.print("[yellow]No sites found in file.[/yellow]")
        return

    table = Table(title=f"Sites to seed ({len(sites)})", show_header=True)
    table.add_column("Name")
    table.add_column("Health URL")
    table.add_column("System URL")
    table.add_column("Environment")
    table.add_column("Enabled")

    for s in sites:
        table.add_row(
            s.get("name", ""),
            s.get("health_url") or "—",
            s.get("system_url") or "—",
            s.get("environment") or s.get("env") or "—",
            "✓" if s.get("enabled", True) else "✗",
        )

    console.print(table)

    if dry_run:
        console.print("[yellow]Dry run — no changes saved.[/yellow]")
        return

    from app.core.database import AsyncSessionLocal
    from app.modules.monitor.db_models import SiteDB
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        created = updated = skipped = 0

        if clear:
            result = await db.execute(select(SiteDB))
            existing_sites = result.scalars().all()
            for site in existing_sites:
                await db.delete(site)
            await db.flush()
            console.print(f"  [red]cleared[/red] {len(existing_sites)} existing sites")

        for s in sites:
            name = s.get("name", "").strip()
            if not name:
                console.print("[yellow]Skipping site with no name.[/yellow]")
                skipped += 1
                continue

            result = await db.execute(select(SiteDB).where(SiteDB.name == name))
            existing = result.scalar_one_or_none()

            fields = {
                "name": name,
                "description": s.get("description"),
                "health_url": s.get("health_url") or None,
                "system_url": s.get("system_url") or None,
                "token": s.get("token") or None,
                "enabled": bool(s.get("enabled", True)),
                "polling_health": int(s.get("polling_health", 300)),
                "polling_system": int(s.get("polling_system", 300)),
                "polling_updates": int(s.get("polling_updates", 43200)),
                "polling_reboot": int(s.get("polling_reboot", 1800)),
                "ssl_check_url": s.get("ssl_check_url") or None,
                "polling_ssl": int(s.get("polling_ssl", 43200)),
                "teams_webhook_url": s.get("teams_webhook_url") or None,
                "server_label": s.get("server") or s.get("server_label") or None,
                "environment": s.get("environment") or s.get("env") or None,
            }

            if existing:
                for k, v in fields.items():
                    setattr(existing, k, v)
                updated += 1
                console.print(f"  [blue]updated[/blue] {name}")
            else:
                db.add(SiteDB(**fields))
                created += 1
                console.print(f"  [green]created[/green] {name}")

        await db.commit()

    console.print(
        f"\n[bold green]Done.[/bold green] "
        f"Created: {created}, Updated: {updated}, Skipped: {skipped}"
    )


@monitor_app.command("sites")
def sites_list(
    wide: bool | None = typer.Option(
        None, "--wide/--no-wide", "-w", help="Show full URLs without truncation"
    ),
) -> None:
    """List all configured sites with their URLs and settings."""
    if wide is None:
        wide = typer.confirm("Show full URLs?", default=False)
    asyncio.run(_sites_list(wide))


async def _sites_list(wide: bool) -> None:
    from app.core.database import AsyncSessionLocal
    from app.modules.monitor.repositories import SiteRepository

    async with AsyncSessionLocal() as db:
        sites = await SiteRepository(db).get_all()

    table = Table(title=f"Sites ({len(sites)})", show_header=True, header_style="bold")
    table.add_column("Name")
    table.add_column("Env")
    if wide:
        table.add_column("Health URL", overflow="fold")
        table.add_column("System URL", overflow="fold")
    else:
        table.add_column("Health URL", overflow="ellipsis", max_width=40)
        table.add_column("System URL", overflow="ellipsis", max_width=40)
    table.add_column("IP override")
    table.add_column("SSL")
    table.add_column("Enabled")

    for site in sites:
        table.add_row(
            site.name,
            site.environment or "—",
            site.health_url or "—",
            site.system_url or "—",
            site.ip or "—",
            "✓" if site.verify_ssl else "[yellow]✗[/yellow]",
            "✓" if site.enabled else "[dim]✗[/dim]",
        )

    console.print(table)


@monitor_app.command("status")
def status(
    errors_only: bool = typer.Option(
        False,
        "--errors-only",
        "-e",
        help="Pokaż tylko strony z błędem, degradacją lub brakiem polla",
    ),
) -> None:
    """Stan ostatniego polla (health + system) dla każdej strony z bazy."""
    asyncio.run(_status(errors_only))


async def _status(errors_only: bool) -> None:
    from app.core.database import AsyncSessionLocal
    from app.modules.monitor.repositories import (
        SiteRepository,
        SnapshotRepository,
    )

    async with AsyncSessionLocal() as db:
        site_repo = SiteRepository(db)
        snap_repo = SnapshotRepository(db)
        sites = await site_repo.get_all()
        site_ids = [s.id for s in sites]
        by_site = await snap_repo.get_latest_for_sites(site_ids)

    table = Table(
        title="Monitor — ostatni snapshot na stronę",
        show_header=True,
        header_style="bold",
    )
    table.add_column("Nazwa")
    table.add_column("Środowisko")
    table.add_column("Health")
    table.add_column("System")
    table.add_column("Cert")
    table.add_column("Błąd", overflow="ellipsis", max_width=_ERR_COL_MAX + 8)
    table.add_column("Ostatni poll")

    for site in sites:
        snaps = by_site.get(site.id, {})
        health_snap = snaps.get("health") if site.health_url else None
        system_snap = snaps.get("system") if site.system_url else None
        ssl_snap = snaps.get("ssl") if site.ssl_check_url else None
        row_style, kind = _row_style_and_kind(site, health_snap, system_snap, ssl_snap)
        if errors_only and not _include_in_errors_only(kind):
            continue

        env = site.environment or "—"
        err_cell = _format_error_cell(health_snap, system_snap, ssl_snap)
        poll_cell = _format_last_poll(health_snap, system_snap, ssl_snap)

        table.add_row(
            site.name,
            env,
            _status_display(health_snap),
            _status_display(system_snap),
            _cert_display(ssl_snap),
            err_cell,
            poll_cell,
            style=row_style,
        )

    console.print(table)
