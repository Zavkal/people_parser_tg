import asyncio
import datetime
import time
from zoneinfo import ZoneInfo

from aiogram import F, Router, types


from bot.keyboards.send_post_keyboard import send_post_base_kb
from bot.middleware.check_media import check_media_post
from database.db import get_all_channel_publish, update_button_states, get_all_publ_time

router = Router(name="Отправка поста в ТГ")
msk_tz = ZoneInfo("Europe/Moscow")


@router.callback_query(F.data.startswith("send_to_tg:"))
async def send_to_tg_handler(callback: types.CallbackQuery) -> None:
    media_id = callback.data.split(':')[-1]
    update_button_states(media_id=media_id, button_tg_state='on')
    time_post = get_all_publ_time(media_id)[0]
    if time_post:
        time_post = datetime.datetime.strptime(time_post, "%Y-%m-%d %H:%M:%S")
        time_now = datetime.datetime.now(msk_tz).replace(tzinfo=None)
        time_post = time_post - time_now
        time_post = time_post.total_seconds()
        await state_time_publish_post(callback, media_id, time_post)
    else:
        await state_time_publish_post(callback, media_id, time_sleep=0.2)
    await callback.message.edit_reply_markup(reply_markup=send_post_base_kb(media_id))


async def state_time_publish_post(callback: types.CallbackQuery, media_id: str, time_sleep: float):
    channels = get_all_channel_publish()
    media_group, all_message = check_media_post(media_id)
    if channels:
        await asyncio.sleep(time_sleep)
        for channel in channels:
            chat_id = channel['channel_id']
            if media_group:
                await callback.bot.send_media_group(media=media_group,
                                                    chat_id=chat_id)
            else:
                await callback.bot.send_message(text=all_message[0]['content'],
                                                chat_id=chat_id)
    else:
        await callback.answer("Нет канала для отправки")
