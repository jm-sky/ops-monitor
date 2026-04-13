"""Monitor management CLI commands."""

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

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
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be imported without saving"
    ),
) -> None:
    """Seed sites from a YAML file (upsert by name)."""
    asyncio.run(_seed_sites(yaml_file, dry_run))


async def _seed_sites(yaml_file: Path, dry_run: bool) -> None:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        console.print("[red]PyYAML not installed. Run: pip install pyyaml[/red]")
        raise typer.Exit(1)

    if not yaml_file.exists():
        console.print(f"[red]File not found: {yaml_file}[/red]")
        raise typer.Exit(1)

    data = yaml.safe_load(yaml_file.read_text())
    sites = data.get("sites", [])

    if not sites:
        console.print("[yellow]No sites found in file.[/yellow]")
        return

    table = Table(title=f"Sites to seed ({len(sites)})", show_header=True)
    table.add_column("Name")
    table.add_column("Health URL")
    table.add_column("System URL")
    table.add_column("Enabled")

    for s in sites:
        table.add_row(
            s.get("name", ""),
            s.get("health_url") or "—",
            s.get("system_url") or "—",
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
                "teams_webhook_url": s.get("teams_webhook_url") or None,
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
