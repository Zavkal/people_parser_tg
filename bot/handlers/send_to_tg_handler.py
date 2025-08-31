import asyncio
import datetime
from zoneinfo import ZoneInfo

from aiogram import F, Router, types


from bot.keyboards.send_post_keyboard import send_post_base_kb
from bot.middleware.check_media import check_media_post
from bot.service.post_to_tg_service import state_time_publish_post
from database.db import get_all_channel_publish, update_button_states, get_all_publ_time

router = Router(name="Отправка поста в ТГ")
msk_tz = ZoneInfo("Europe/Moscow")


@router.callback_query(F.data.startswith("send_to_tg:"))
async def send_to_tg_handler(callback: types.CallbackQuery) -> None:
    media_id = callback.data.split(':')[-1]
    update_button_states(media_id=media_id, button_tg_state='on')
    await callback.message.edit_reply_markup(reply_markup=send_post_base_kb(media_id))
    time_post = get_all_publ_time(media_id)[0]
    if time_post:
        time_post = datetime.datetime.strptime(time_post, "%Y-%m-%d %H:%M:%S")
        time_now = datetime.datetime.now(msk_tz).replace(tzinfo=None)
        time_post = time_post - time_now
        time_post = time_post.total_seconds()
        await state_time_publish_post(
            media_id=media_id,
            time_sleep=time_post,
            call_or_msg=callback,
        )
    else:
        await state_time_publish_post(
            media_id=media_id,
            time_sleep=1,
            call_or_msg=callback,
        )



