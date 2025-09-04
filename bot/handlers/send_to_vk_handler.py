import asyncio
from zoneinfo import ZoneInfo

from aiogram import F, Router, types

from bot.keyboards.send_post_keyboard import send_post_base_kb
from bot.middleware.send_to_vk_options import  post_to_wall_vk
from database.db import update_button_states

router = Router(name="Отправка поста в ВК")
msk_tz = ZoneInfo("Europe/Moscow")


@router.callback_query(F.data.startswith("send_to_vk:"))
async def send_to_vk_handler(callback: types.CallbackQuery) -> None:
    media_id = callback.data.split(':')[1]

    update_button_states(media_id=media_id, button_vk_state='on')

    await callback.message.edit_reply_markup(reply_markup=send_post_base_kb(media_id))

    try:
        await post_to_wall_vk(
            media_id=media_id,
            call_or_msg=callback,
        )

    except Exception as e:
        mess_del = await callback.bot.send_message(
            text=f"🛑Ошибка при отправлении данных, попробуйте снова. Проверьте стену ВКонтакте! Ошибка: {e}🛑",
            chat_id=callback.message.chat.id)
        await asyncio.sleep(4)
        await callback.bot.delete_message(chat_id=mess_del.chat.id,
                                          message_id=mess_del.message_id)
        update_button_states(media_id=media_id, button_vk_state='off')
        await callback.message.edit_reply_markup(reply_markup=send_post_base_kb(media_id))

    mess_del = await callback.bot.send_message(
        text="⚠️ Все данные успешно скачаны и загружены на сервер вконтакте для публикации.",
        chat_id=callback.message.chat.id)
    await asyncio.sleep(4)
    await callback.bot.delete_message(chat_id=mess_del.chat.id,
                                      message_id=mess_del.message_id)


@router.callback_query(F.data.startswith("send_to_vk_error_close:"))
async def send_to_vk_handler_error(callback: types.CallbackQuery, ) -> None:
    media_id = callback.data.split(':')[1]
    update_button_states(media_id=media_id, button_vk_state='off')
    await callback.message.edit_reply_markup(reply_markup=send_post_base_kb(media_id))
