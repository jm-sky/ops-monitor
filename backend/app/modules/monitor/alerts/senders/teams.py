"""MS Teams alert sender via Incoming Webhook (Adaptive Cards)."""

import logging
from typing import Any

import httpx

from .base import AlertPayload, BaseSender

logger = logging.getLogger(__name__)


class TeamsSender(BaseSender):
    async def send(self, config: dict[str, Any], payload: AlertPayload) -> None:
        webhook_url = config.get("webhook_url", "")
        if not webhook_url:
            raise ValueError("Teams channel missing webhook_url")

        card = _build_adaptive_card(payload)
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(webhook_url, json=card)
            resp.raise_for_status()

    async def test(self, config: dict[str, Any]) -> str:
        webhook_url = config.get("webhook_url", "")
        if not webhook_url:
            raise ValueError("Missing webhook_url")

        test_payload = AlertPayload(
            site_name="test-site",
            alert_type="health",
            status="ok",
            detail="This is a test alert from Ops Monitor.",
        )
        await self.send(config, test_payload)
        return "Test message sent to Teams"


def _build_adaptive_card(payload: AlertPayload) -> dict[str, Any]:
    color = "attention" if payload.status in ("failed", "degraded") else "good"
    return {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "msteams": {"width": "Full"},
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": payload.title,
                            "weight": "Bolder",
                            "size": "Medium",
                            "color": color,
                        },
                        {
                            "type": "TextBlock",
                            "text": payload.body,
                            "wrap": True,
                        },
                    ],
                },
            }
        ],
    }
