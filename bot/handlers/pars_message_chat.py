from aiogram import F, Router, types

from bot.handlers.start_handler import start_bot_edit_post
from bot.middleware.album_middleware import AlbumMiddleware
from bot.middleware.message_type import message_media_type
from database.db import add_post_media, select_chat, select_samples

router = Router(name="Взятие поста в работу")
router.message.middleware(AlbumMiddleware(latency=0.3))


CHAT_ID = int(select_chat()[0])


@router.message(F.chat.id == CHAT_ID)
async def handle_media_group(message: types.Message, album: list = None):
    samples = select_samples()
    if album:
        for message in album:
            content = message.html_text
            if len(content) > 1 and samples:
                for sample in samples:
                    sample = sample[1]
                    if sample in content:
                        content = content.replace(sample, '')
            content = content.replace('  ', ' ')
            content = content.strip()
            media_id = message.media_group_id
            message_id = message.message_id
            file_id, media_type, format_file = message_media_type(message)
            add_post_media(media_id, message_id, content, file_id, media_type, format_file)
        await start_bot_edit_post(message, media_id)

    else:

        message_id = message.message_id
        media_id = message.message_id
        file_id, media_type, format_file = message_media_type(message)
        content = message.html_text
        if len(content) > 1 and samples:
            for sample in samples:
                sample = sample[1]
                if sample in content:
                    content = content.replace(sample, '')
        content = content.replace('  ', ' ')
        content = content.strip()
        add_post_media(media_id, message_id, content, file_id, media_type, format_file)
        await start_bot_edit_post(message, media_id)




