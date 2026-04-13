"""Email alert sender using the existing core email service."""

import logging
from typing import Any

from app.core.email import get_email_service

from .base import AlertPayload, BaseSender

logger = logging.getLogger(__name__)


class EmailSender(BaseSender):
    async def send(self, config: dict[str, Any], payload: AlertPayload) -> None:
        recipients: list[str] = config.get("to", [])
        if not recipients:
            raise ValueError("Email channel missing 'to' list")

        prefix: str = config.get("subject_prefix", "[OpsMonitor]")
        subject = f"{prefix} {payload.title}"
        html_body = _html(payload)
        text_body = payload.body

        email_service = get_email_service()
        for recipient in recipients:
            success = await email_service.adapter.send_email(
                to=recipient,
                subject=subject,
                html_body=html_body,
                text_body=text_body,
            )
            if not success:
                raise RuntimeError(f"Failed to send alert email to {recipient}")

    async def test(self, config: dict[str, Any]) -> str:
        recipients: list[str] = config.get("to", [])
        if not recipients:
            raise ValueError("Missing 'to' list")

        test_payload = AlertPayload(
            site_name="test-site",
            alert_type="health",
            status="ok",
            detail="This is a test alert from Ops Monitor.",
        )
        await self.send(config, test_payload)
        return f"Test email sent to {', '.join(recipients)}"


def _html(payload: AlertPayload) -> str:
    color = "#dc2626" if payload.status in ("failed", "degraded") else "#16a34a"
    detail_row = (
        f"<p style='color:#6b7280'>{payload.detail}</p>" if payload.detail else ""
    )
    return f"""
<div style="font-family:sans-serif;max-width:600px;margin:0 auto">
  <h2 style="color:{color}">{payload.title}</h2>
  <p>Site <strong>{payload.site_name}</strong> — {payload.status_label}</p>
  {detail_row}
  <hr style="border:none;border-top:1px solid #e5e7eb;margin:16px 0">
  <p style="color:#9ca3af;font-size:12px">Ops Monitor</p>
</div>
""".strip()
