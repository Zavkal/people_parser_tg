from aiogram import F, Router, types

from bot.keyboards.send_post_keyboard import send_post_base_kb
from bot.middleware.check_media import check_media_post
from database.db import get_all_channel_publish, update_button_states

router = Router(name="Отправка поста в ТГ")


@router.callback_query(F.data.startswith("send_to_tg:"))
async def send_to_tg_handler(callback: types.CallbackQuery,) -> None:
    media_id = callback.data.split(':')[-1]
    channels = get_all_channel_publish()
    media_group, all_message = check_media_post(media_id)
    update_button_states(media_id=media_id, button_tg_state='on')
    for channel in channels:
        chat_id = channel['channel_id']
        if media_group:
            await callback.bot.send_media_group(media=media_group,
                                                chat_id=chat_id)
        else:
            await callback.bot.send_message(text=all_message[0]['content'],
                                            chat_id=chat_id)

    await callback.message.edit_reply_markup(reply_markup=send_post_base_kb(media_id))
