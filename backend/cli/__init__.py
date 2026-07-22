"""CLI package for Ops Monitor management commands."""

from .commands import db_app, monitor_app, test_app, users_app
from .main import app, main

app.add_typer(db_app, name="db")
app.add_typer(users_app, name="users")
app.add_typer(test_app, name="test")
app.add_typer(monitor_app, name="monitor")

__all__ = ["app", "main"]
