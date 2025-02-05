from aiogram import F, Router, types

from bot.handlers.start_handler import start_bot_edit_post
from bot.middleware.album_middleware import AlbumMiddleware
from bot.middleware.message_type import message_media_type
from database.db import add_post_media, select_chat, select_samples

router = Router(name="Взятие поста в работу")
router.message.middleware(AlbumMiddleware(latency=0.3))

try:
    data_middleware = select_chat()
    CHAT_ID = int(data_middleware[0]) if data_middleware else None
except Exception as e:
    CHAT_ID = None
    print(f"Ошибка при загрузке чата: {e}")

# Хранилище обработанных сообщений
processed_messages = set()

if CHAT_ID:
    @router.message(F.chat.id == CHAT_ID)
    async def handle_media_group(message: types.Message, album: list = None):
        samples = select_samples()

        if album:
            media_id = album[0].media_group_id
            if media_id in processed_messages:
                return  # Уже обработано

            processed_messages.add(media_id)
            for msg in album:
                content = msg.html_text or ""
                if samples:
                    for sample in samples:
                        sample = sample[1]
                        if sample in content:
                            content = content.replace(sample, '')
                content = content.replace('  ', ' ').strip()
                file_id, media_type, format_file = message_media_type(msg)
                add_post_media(media_id, msg.message_id, content, file_id, media_type, format_file)

            await start_bot_edit_post(message, media_id)
        else:
            if message.message_id in processed_messages:
                return  # Уже обработано

            processed_messages.add(message.message_id)
            content = message.html_text or ""
            if samples:
                for sample in samples:
                    sample = sample[1]
                    if sample in content:
                        content = content.replace(sample, '')
            content = content.replace('  ', ' ').strip()
            file_id, media_type, format_file = message_media_type(message)
            add_post_media(message.message_id, message.message_id, content, file_id, media_type, format_file)
            await start_bot_edit_post(message, message.message_id)
