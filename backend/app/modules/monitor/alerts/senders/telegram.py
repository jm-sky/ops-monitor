"""Telegram Bot alert sender via sendMessage API."""

import logging
from typing import Any

import httpx

from .base import AlertPayload, BaseSender

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


class TelegramSender(BaseSender):
    async def send(self, config: dict[str, Any], payload: AlertPayload) -> None:
        bot_token = config.get("bot_token", "")
        chat_id = config.get("chat_id", "")
        if not bot_token or not chat_id:
            raise ValueError("Telegram channel missing bot_token or chat_id")

        text = _format_message(payload)
        url = TELEGRAM_API.format(token=bot_token)

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            )
            data = resp.json()
            if not data.get("ok"):
                raise RuntimeError(
                    f"Telegram API error: {data.get('description', 'unknown')}"
                )

    async def test(self, config: dict[str, Any]) -> str:
        test_payload = AlertPayload(
            site_name="test-site",
            alert_type="health",
            status="ok",
            detail="This is a test alert from Ops Monitor.",
        )
        await self.send(config, test_payload)
        return "Test message sent to Telegram"


def _format_message(payload: AlertPayload) -> str:
    lines = [f"<b>{payload.title}</b>", f"Site: <code>{payload.site_name}</code>"]
    if payload.detail:
        lines.append(payload.detail)
    return "\n".join(lines)
