import asyncio

from aiogram import types

from bot.middleware.check_media import check_media_post
from database.db import get_all_channel_publish


async def state_time_publish_post(
        media_id: str,
        time_sleep: float,
        call_or_msg: types.CallbackQuery | types.Message = None,
) -> None:

    channels = get_all_channel_publish()

    media_group, all_message = check_media_post(media_id)

    if channels:
        await asyncio.sleep(time_sleep)

        for channel in channels:
            chat_id = channel['channel_id']

            if media_group:
                await call_or_msg.bot.send_media_group(media=media_group,
                                                    chat_id=chat_id)
            else:
                await call_or_msg.bot.send_message(text=all_message[0]['content'],
                                                chat_id=chat_id)
    else:
        await call_or_msg.answer("Нет канала для отправки")
