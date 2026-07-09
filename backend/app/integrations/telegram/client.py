"""Async HTTP client for Telegram Bot API."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import Settings

logger = logging.getLogger(__name__)


class TelegramAPIError(Exception):
    def __init__(self, message: str, *, status_code: int | None = None, description: str | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.description = description


class TelegramClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "TelegramClient":
        self._client = httpx.AsyncClient(timeout=self._settings.TELEGRAM_HTTP_TIMEOUT)
        return self

    async def __aexit__(self, *args: object) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _token(self) -> str:
        token = self._settings.TELEGRAM_BOT_TOKEN.strip()
        if not token:
            raise TelegramAPIError("TELEGRAM_BOT_TOKEN not configured", status_code=401)
        return token

    def _api_base(self) -> str:
        return self._settings.TELEGRAM_API_BASE_URL.rstrip("/")

    async def send_message(
        self,
        chat_id: str | int,
        text: str,
        *,
        parse_mode: str = "HTML",
        disable_web_page_preview: bool = False,
    ) -> dict[str, Any]:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._settings.TELEGRAM_HTTP_TIMEOUT)
        url = f"{self._api_base()}/bot{self._token()}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }
        response = await self._client.post(url, json=payload)
        data = response.json()
        if response.status_code >= 400 or not data.get("ok"):
            description = None
            if isinstance(data.get("description"), str):
                description = data["description"]
            raise TelegramAPIError(
                description or f"Telegram API error HTTP {response.status_code}",
                status_code=response.status_code,
                description=description,
            )
        result = data.get("result")
        return result if isinstance(result, dict) else {}

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
