from aiogram import F, Router, types
from aiogram.types import ContentType

from bot.handlers.start_handler import command_start_handler
from bot.keyboards.base_post_working_keyboard import base_post_working_kb
from bot.middleware.album_middleware import AlbumMiddleware
from database.db import add_post_media

router = Router(name="Взятие поста в работу")
router.message.middleware(AlbumMiddleware(latency=0.3))


CHAT_ID = -1002324214689  # Укажите ID чата


@router.message(F.chat.id == CHAT_ID)
async def handle_media_group(message: types.Message, album: list = None):
    # Идентификатор медиагруппы
    if album:
        for message in album:
            media_id = message.media_group_id
            message_id = message.message_id
            content = message.caption or message.text or ''
            file_id, media_type, format_file = message_media_type(message)

            add_post_media(media_id, message_id, content, file_id, media_type, format_file)
        await command_start_handler(message, media_id)

    else:
        message_id = message.message_id
        media_id = message.message_id
        content = message.text or message.caption or ''
        file_id, media_type, format_file = message_media_type(message)
        add_post_media(media_id, message_id, content, file_id, media_type, format_file)
        await command_start_handler(message, media_id)


def message_media_type(message: types.Message):
    file_id, media_type, format_file = None, None, None
    if message.photo:
        file_id = message.photo[-1].file_id
        media_type = 'photo'
        format_file = '.jpg'
    elif message.video:
        file_id = message.video.file_id
        media_type = 'video'
        format_file = '.mp4'
    elif message.document:
        file_id = message.document.file_id
        media_type = 'document'
        format_file = message.document.file_name
    elif message.animation:
        file_id = message.animation.file_id
        media_type = 'animation'
        format_file = message.animation.file_name
    try:
        return file_id, media_type, format_file
    except:
        return

