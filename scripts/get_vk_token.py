#!/usr/bin/env python3
"""
CLI для получения VK ID токена (PKCE).

Примеры:
  python scripts/get_vk_token.py start
  python scripts/get_vk_token.py exchange "https://xbox-rent.ru/?code=...&device_id=...&state=..."
  python scripts/get_vk_token.py refresh
  python scripts/get_vk_token.py test
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from bot.service.vk_id_token_service import VkIdTokenService  # noqa: E402
from database.db import create_vk_id_tables  # noqa: E402


def cmd_start(service: VkIdTokenService) -> None:
    url, session = service.start_authorization()
    print("\n=== Шаг 1: откройте ссылку в браузере ===\n")
    print(url)
    print("\n=== Шаг 2: после «Разрешить» скопируйте полный URL из адресной строки ===\n")
    print(
        "Выполните:\n"
        f'  python scripts/get_vk_token.py exchange "ВСТАВЬТЕ_URL_СЮДА"\n'
    )
    print(f"state (для проверки): {session.state}\n")


def cmd_exchange(service: VkIdTokenService, callback: str, write_env: bool) -> None:
    tokens = service.exchange_code(callback)
    print("\n=== Токены получены ===\n")
    print(json.dumps(
        {
            "access_token": tokens.access_token[:20] + "...",
            "refresh_token": (tokens.refresh_token[:20] + "...") if tokens.refresh_token else None,
            "expires_in": tokens.expires_in,
            "user_id": tokens.user_id,
            "scope": tokens.scope,
            "device_id": tokens.device_id,
        },
        ensure_ascii=False,
        indent=2,
    ))

    if write_env:
        service.save_to_env(tokens)
        print("\nЗаписано в .env: VK_USER_TOKEN, VK_REFRESH_TOKEN, VK_DEVICE_ID")

    api_result = service.test_vk_api(tokens.access_token)
    print("\n=== Проверка api.vk.com/method/video.save ===\n")
    print(json.dumps(api_result, ensure_ascii=False, indent=2))

    if "error" in api_result:
        err = api_result["error"]
        print(
            f"\nВнимание: VK API вернул ошибку {err.get('error_code')}: {err.get('error_msg')}\n"
            "Токен VK ID получен, но для video.save/wall.post могут понадобиться "
            "расширенные права в настройках приложения VK ID.\n"
        )


def cmd_refresh(service: VkIdTokenService, write_env: bool) -> None:
    tokens = service.refresh_access_token()
    print("Access token обновлён.")
    if write_env:
        service.save_to_env(tokens)
        print("Записано в .env")


def cmd_test(service: VkIdTokenService) -> None:
    import os
    token = os.getenv("VK_USER_TOKEN", "")
    if not token:
        raise SystemExit("VK_USER_TOKEN не задан в .env")
    result = service.test_vk_api(token)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Получение токена VK ID (PKCE)")
    parser.add_argument(
        "command",
        choices=("start", "exchange", "refresh", "test"),
        help="start — ссылка для браузера; exchange — обмен code; refresh — обновить токен",
    )
    parser.add_argument(
        "callback",
        nargs="?",
        help="URL редиректа после авторизации (для exchange)",
    )
    parser.add_argument(
        "--no-env",
        action="store_true",
        help="Не записывать токены в .env",
    )
    args = parser.parse_args()

    create_vk_id_tables()
    service = VkIdTokenService()
    write_env = not args.no_env

    if args.command == "start":
        cmd_start(service)
    elif args.command == "exchange":
        if not args.callback:
            raise SystemExit('Укажите URL: python scripts/get_vk_token.py exchange "https://..."')
        cmd_exchange(service, args.callback, write_env)
    elif args.command == "refresh":
        cmd_refresh(service, write_env)
    elif args.command == "test":
        cmd_test(service)


if __name__ == "__main__":
    main()
