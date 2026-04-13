"""Base class for alert senders."""

from abc import ABC, abstractmethod
from typing import Any


class AlertPayload:
    def __init__(
        self,
        site_name: str,
        alert_type: str,
        status: str,
        detail: str | None = None,
    ) -> None:
        self.site_name = site_name
        self.alert_type = alert_type
        self.status = status
        self.detail = detail

    @property
    def title(self) -> str:
        icons = {
            "health": "🔴" if self.status in ("failed", "degraded") else "🟢",
            "reboot": "🔁",
            "updates": "📦",
        }
        icon = icons.get(self.alert_type, "⚠️")
        return f"{icon} [{self.site_name}] {self.status_label}"

    @property
    def status_label(self) -> str:
        labels = {
            "ok": "OK",
            "degraded": "Degraded",
            "failed": "FAILED",
            "reboot_required": "Reboot required",
            "outdated": "Updates available",
        }
        return labels.get(self.status, self.status)

    @property
    def body(self) -> str:
        parts = [f"Site **{self.site_name}** — {self.status_label}"]
        if self.detail:
            parts.append(self.detail)
        return "\n".join(parts)


class BaseSender(ABC):
    @abstractmethod
    async def send(self, config: dict[str, Any], payload: AlertPayload) -> None:
        """Send an alert. Raise on failure."""
        ...

    @abstractmethod
    async def test(self, config: dict[str, Any]) -> str:
        """Send a test message. Return success description or raise."""
        ...
