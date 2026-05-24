Проект старый, говнокода куча. Логика с взаимодействием постов очень сложная. 

FAQ — токен VK ID:

1. В `.env`: `VK_CLIENT_ID`, `VK_REDIRECT_URI` (как в кабинете VK ID), `GROUP_VK_ID`.
2. Запуск:
   ```bash
   python scripts/get_vk_token.py start
   ```
3. Открыть ссылку в браузере → «Разрешить» → скопировать URL редиректа.
4. Обменять код на токен (запишет в `.env`):
   ```bash
   python scripts/get_vk_token.py exchange "https://xbox-rent.ru/?code=...&device_id=...&state=..."
   ```
5. Один раз обменять код — дальше бот сам обновляет токен по `refresh_token` (фоновая задача каждые 5 мин, за 10 мин до истечения).

Сессия OAuth и токены хранятся в SQLite (`vk_id_oauth_session`, `vk_id_tokens`). Таблицы создаются при старте бота в `start_db()`.

Ручное обновление (если нужно):
```bash
python scripts/get_vk_token.py refresh
```

Документация: [API VK ID](https://id.vk.com/about/business/go/docs/ru/vkid/latest/vk-id/connection/api-description)