"""CLI package for Ops Monitor management commands."""

from .main import app, main
from .commands import db_app, test_app, users_app

app.add_typer(db_app, name="db")
app.add_typer(users_app, name="users")
app.add_typer(test_app, name="test")

__all__ = ["app", "main"]
