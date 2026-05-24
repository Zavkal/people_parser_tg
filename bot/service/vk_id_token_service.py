"""
Получение токенов VK ID (PKCE) по документации:
https://id.vk.com/about/business/go/docs/ru/vkid/latest/vk-id/connection/api-description
"""

from __future__ import annotations

import base64
import hashlib
import os
import re
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from dotenv import load_dotenv

from database.db import (
    get_vk_id_oauth_session,
    get_vk_id_tokens,
    save_vk_id_oauth_session,
    save_vk_id_tokens,
)

load_dotenv()

AUTHORIZE_URL = "https://id.vk.ru/authorize"
TOKEN_URL = "https://id.vk.ru/oauth2/auth"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


@dataclass
class OAuthPendingSession:
    code_verifier: str
    state: str
    client_id: str
    redirect_uri: str
    scope: str

    def save(self) -> None:
        save_vk_id_oauth_session(
            code_verifier=self.code_verifier,
            state=self.state,
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
        )

    @classmethod
    def load(cls) -> OAuthPendingSession:
        data = get_vk_id_oauth_session()
        if not data:
            raise FileNotFoundError(
                "Нет сессии OAuth в БД. Сначала выполните: python scripts/get_vk_token.py start"
            )
        return cls(**data)


@dataclass
class VkIdTokens:
    access_token: str
    refresh_token: str | None
    expires_in: int | None
    user_id: int | None
    scope: str | None
    device_id: str | None
    token_type: str | None = None
    id_token: str | None = None
    client_id: str | None = None

    @classmethod
    def from_response(
        cls,
        payload: dict[str, Any],
        device_id: str | None = None,
        client_id: str | None = None,
    ) -> VkIdTokens:
        if "error" in payload:
            desc = payload.get("error_description", payload["error"])
            raise RuntimeError(f"VK ID: {payload['error']} — {desc}")
        return cls(
            access_token=payload["access_token"],
            refresh_token=payload.get("refresh_token"),
            expires_in=payload.get("expires_in"),
            user_id=payload.get("user_id"),
            scope=payload.get("scope"),
            device_id=device_id or payload.get("device_id"),
            token_type=payload.get("token_type"),
            id_token=payload.get("id_token"),
            client_id=client_id,
        )

    @classmethod
    def from_db(cls, data: dict[str, Any]) -> VkIdTokens:
        return cls(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_in=data.get("expires_in"),
            user_id=data.get("user_id"),
            scope=data.get("scope"),
            device_id=data.get("device_id"),
            token_type=data.get("token_type"),
            id_token=data.get("id_token"),
            client_id=data.get("client_id"),
        )


def _generate_code_verifier() -> str:
    while True:
        verifier = secrets.token_urlsafe(64)
        if 43 <= len(verifier) <= 128 and re.fullmatch(r"[a-zA-Z0-9_\-]+", verifier):
            return verifier


def _generate_code_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def _generate_state() -> str:
    while True:
        state = secrets.token_urlsafe(48)
        if len(state) >= 32 and re.fullmatch(r"[a-zA-Z0-9_\-]+", state):
            return state


def parse_redirect_callback(callback: str) -> dict[str, str]:
    """Парсит полный URL редиректа или query-строку (?code=...&device_id=...)."""
    text = callback.strip()
    if text.startswith("?"):
        text = f"https://local.invalid/{text}"
    elif "://" not in text:
        text = f"https://local.invalid/?{text.lstrip('?')}"

    parsed = urlparse(text)
    params = {k: v[0] for k, v in parse_qs(parsed.query).items()}

    if "error" in params:
        raise RuntimeError(
            f"VK ID вернул ошибку: {params.get('error')} — {params.get('error_description', '')}"
        )
    return params


class VkIdTokenService:
    def __init__(
        self,
        client_id: str | None = None,
        redirect_uri: str | None = None,
        scope: str | None = None,
    ) -> None:
        self.client_id = client_id or os.getenv("VK_CLIENT_ID", "")
        self.redirect_uri = redirect_uri or os.getenv("VK_REDIRECT_URI", "")
        self.scope = scope or os.getenv(
            "VK_ID_SCOPE",
            "vkid.personal_info wall photos video groups offline",
        )

        if not self.client_id:
            raise ValueError("Укажите VK_CLIENT_ID в .env")
        if not self.redirect_uri:
            raise ValueError("Укажите VK_REDIRECT_URI в .env (как в настройках приложения VK ID)")

    def start_authorization(self) -> tuple[str, OAuthPendingSession]:
        code_verifier = _generate_code_verifier()
        code_challenge = _generate_code_challenge(code_verifier)
        state = _generate_state()

        session = OAuthPendingSession(
            code_verifier=code_verifier,
            state=state,
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
        )
        session.save()

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "scope": self.scope,
        }
        url = f"{AUTHORIZE_URL}?{urlencode(params)}"
        return url, session

    def exchange_code(
        self,
        callback: str,
        session: OAuthPendingSession | None = None,
    ) -> VkIdTokens:
        session = session or OAuthPendingSession.load()
        params = parse_redirect_callback(callback)

        code = params.get("code")
        device_id = params.get("device_id")
        returned_state = params.get("state")

        if not code:
            raise ValueError("В callback нет параметра code")
        if not device_id:
            raise ValueError("В callback нет параметра device_id")
        if returned_state != session.state:
            raise ValueError("state не совпадает — возможна подмена ответа")

        body = {
            "grant_type": "authorization_code",
            "code_verifier": session.code_verifier,
            "redirect_uri": session.redirect_uri,
            "code": code,
            "client_id": session.client_id,
            "device_id": device_id,
            "state": session.state,
        }
        response = requests.post(TOKEN_URL, data=body, timeout=30)
        response.raise_for_status()
        tokens = VkIdTokens.from_response(
            response.json(),
            device_id=device_id,
            client_id=session.client_id,
        )
        self._save_tokens_to_db(tokens)
        return tokens

    def refresh_access_token(
        self,
        refresh_token: str | None = None,
        device_id: str | None = None,
        state: str | None = None,
    ) -> VkIdTokens:
        stored = get_vk_id_tokens(self.client_id)
        refresh_token = (
            refresh_token
            or os.getenv("VK_REFRESH_TOKEN")
            or (stored.get("refresh_token") if stored else None)
        )
        device_id = (
            device_id
            or os.getenv("VK_DEVICE_ID")
            or (stored.get("device_id") if stored else None)
        )
        if not refresh_token:
            raise ValueError("Нет refresh_token (БД и .env)")
        if not device_id:
            raise ValueError("Нет device_id (БД и .env)")

        oauth_state = state or _generate_state()
        body = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "device_id": device_id,
            "state": oauth_state,
        }
        if self.scope:
            body["scope"] = self.scope

        response = requests.post(TOKEN_URL, data=body, timeout=30)
        response.raise_for_status()
        tokens = VkIdTokens.from_response(
            response.json(),
            device_id=device_id,
            client_id=self.client_id,
        )
        self._save_tokens_to_db(tokens)
        return tokens

    def get_stored_tokens(self) -> VkIdTokens | None:
        data = get_vk_id_tokens(self.client_id)
        if not data:
            return None
        return VkIdTokens.from_db(data)

    def test_vk_api(self, access_token: str, group_id: str | None = None) -> dict[str, Any]:
        """Проверка, что токен работает с api.vk.com (video.save)."""
        group_id = group_id or os.getenv("GROUP_VK_ID", "")
        if not group_id:
            raise ValueError("Укажите GROUP_VK_ID в .env для проверки")

        response = requests.get(
            "https://api.vk.com/method/video.save",
            params={
                "access_token": access_token,
                "group_id": group_id,
                "v": "5.199",
            },
            timeout=30,
        )
        return response.json()

    def save_to_env(self, tokens: VkIdTokens, env_path: Path = ENV_FILE) -> None:
        if not env_path.is_file():
            raise FileNotFoundError(f"Не найден {env_path}")

        content = env_path.read_text(encoding="utf-8")
        updates = {
            "VK_USER_TOKEN": tokens.access_token,
            "VK_REFRESH_TOKEN": tokens.refresh_token or "",
            "VK_DEVICE_ID": tokens.device_id or "",
            "VK_CLIENT_ID": self.client_id,
            "VK_REDIRECT_URI": self.redirect_uri,
        }

        for key, value in updates.items():
            pattern = rf"^{re.escape(key)}=.*$"
            line = f"{key}={value}"
            if re.search(pattern, content, flags=re.MULTILINE):
                content = re.sub(pattern, line, content, count=1, flags=re.MULTILINE)
            else:
                content = content.rstrip("\n") + f"\n{line}\n"

        env_path.write_text(content, encoding="utf-8")

    def _save_tokens_to_db(self, tokens: VkIdTokens) -> None:
        save_vk_id_tokens(
            client_id=tokens.client_id or self.client_id,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            expires_in=tokens.expires_in,
            user_id=tokens.user_id,
            scope=tokens.scope,
            device_id=tokens.device_id,
            token_type=tokens.token_type,
            id_token=tokens.id_token,
        )
