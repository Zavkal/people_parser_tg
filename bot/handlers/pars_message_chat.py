from aiogram import F, Router, types

from bot.handlers.start_handler import command_start_handler
from bot.middleware.album_middleware import AlbumMiddleware
from bot.middleware.message_type import message_media_type
from database.db import add_post_media

router = Router(name="Взятие поста в работу")
router.message.middleware(AlbumMiddleware(latency=0.3))


CHAT_ID = -1002324214689  # Укажите ID чата


@router.message(F.chat.id == CHAT_ID)
async def handle_media_group(message: types.Message, album: list = None):
    user_id = str(message.from_user.id)
    if album:
        for message in album:
            media_id = message.media_group_id
            message_id = message.message_id
            content = message.caption or message.text or ''
            file_id, media_type, format_file = message_media_type(message)

            add_post_media(media_id, message_id, content, file_id, media_type, format_file, user_id)
        await command_start_handler(message, media_id)

    else:
        message_id = message.message_id
        media_id = message.message_id
        content = message.text or message.caption or ''
        file_id, media_type, format_file = message_media_type(message)
        add_post_media(media_id, message_id, content, file_id, media_type, format_file, user_id)
        await command_start_handler(message, media_id)




