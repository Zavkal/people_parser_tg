from aiogram import F, Router, types

from bot.keyboards.send_post_keyboard import send_post_base_kb
from database.db import update_button_states

router = Router(name="Отправка поста в ВК")


@router.callback_query(F.data.startswith("send_to_vk:"))
async def send_to_vk_handler(callback: types.CallbackQuery,) -> None:
    media_id = callback.data.split(':')[-1]
    update_button_states(media_id=media_id, button_vk_state='on')
    await callback.message.edit_reply_markup(reply_markup=send_post_base_kb(media_id))
