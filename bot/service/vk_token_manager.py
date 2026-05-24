"""
Автообновление VK ID access_token по refresh_token из БД.
"""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timedelta

import vk_api
from dotenv import load_dotenv

from bot.service.vk_id_token_service import VkIdTokenService
from database.db import get_vk_id_tokens

load_dotenv()

logger = logging.getLogger(__name__)

# access_token VK ID живёт ~1 час; обновляем заранее
REFRESH_MARGIN = timedelta(minutes=10)
CHECK_INTERVAL_SEC = 300
DEFAULT_EXPIRES_IN = 3600


class VkTokenManager:
    def __init__(self) -> None:
        self._client_id = os.getenv("VK_CLIENT_ID", "")
        self._vk_session: vk_api.VkApi | None = None
        self._vk = None
        self._current_token: str | None = None
        self._refresh_task: asyncio.Task | None = None
        self._service: VkIdTokenService | None = None

    def _get_service(self) -> VkIdTokenService:
        if self._service is None:
            self._service = VkIdTokenService()
        return self._service

    def _token_expires_at(self, stored: dict) -> datetime | None:
        updated_at = stored.get("updated_at")
        expires_in = stored.get("expires_in") or DEFAULT_EXPIRES_IN
        if not updated_at:
            return None
        try:
            updated = datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None
        return updated + timedelta(seconds=int(expires_in))

    def _needs_refresh(self, stored: dict | None) -> bool:
        if not stored or not stored.get("refresh_token"):
            return False
        expires_at = self._token_expires_at(stored)
        if expires_at is None:
            return True
        return datetime.now() >= expires_at - REFRESH_MARGIN

    def refresh_if_needed(self, force: bool = False) -> str | None:
        """Обновляет токен при необходимости. Возвращает актуальный access_token."""
        if not self._client_id:
            token = os.getenv("VK_USER_TOKEN")
            if token:
                self._apply_token(token)
            return token

        stored = get_vk_id_tokens(self._client_id)
        if not stored:
            token = os.getenv("VK_USER_TOKEN")
            if token:
                self._apply_token(token)
                logger.warning(
                    "Токенов VK ID нет в БД — используется VK_USER_TOKEN из .env. "
                    "Выполните scripts/get_vk_token.py exchange для автообновления."
                )
            return token

        access_token = stored.get("access_token")
        if not force and not self._needs_refresh(stored):
            if access_token:
                self._apply_token(access_token)
            return access_token

        if not stored.get("refresh_token"):
            if access_token:
                self._apply_token(access_token)
            logger.warning("Нет refresh_token — автообновление недоступно")
            return access_token

        try:
            tokens = self._get_service().refresh_access_token()
            self._get_service().save_to_env(tokens)
            self._apply_token(tokens.access_token)
            logger.info("VK access_token обновлён автоматически")
            return tokens.access_token
        except Exception as exc:
            logger.error("Не удалось обновить VK токен: %s", exc)
            if access_token:
                self._apply_token(access_token)
            return access_token

    def _apply_token(self, token: str) -> None:
        if self._current_token == token and self._vk is not None:
            return
        self._current_token = token
        self._vk_session = vk_api.VkApi(token=token)
        self._vk = self._vk_session.get_api()

    def get_api(self):
        self.refresh_if_needed()
        if self._vk is None:
            token = os.getenv("VK_USER_TOKEN")
            if not token:
                raise RuntimeError(
                    "Нет VK токена. Запустите: python scripts/get_vk_token.py start"
                )
            self._apply_token(token)
        return self._vk

    async def ensure_access_token_async(self) -> str | None:
        return await asyncio.to_thread(self.refresh_if_needed)

    async def startup(self) -> None:
        await self.ensure_access_token_async()

    def start_background_task(self) -> None:
        if self._refresh_task and not self._refresh_task.done():
            return
        self._refresh_task = asyncio.create_task(self._refresh_loop())

    async def _refresh_loop(self) -> None:
        while True:
            await asyncio.sleep(CHECK_INTERVAL_SEC)
            try:
                await asyncio.to_thread(self.refresh_if_needed)
            except Exception as exc:
                logger.error("Ошибка фонового обновления VK токена: %s", exc)


vk_token_manager = VkTokenManager()
