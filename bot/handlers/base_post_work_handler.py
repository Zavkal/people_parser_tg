from aiogram import F, Router, types

from bot.keyboards.base_post_working_keyboard import base_post_working_kb
from bot.middleware.autodel_create_message import autodel_create_mg
from bot.middleware.check_media import check_media_post
from database.db import add_message_post, add_button_states

router = Router(name="Начальная работа с постом")


@router.callback_query(F.data.startswith("start_working:"))
async def base_post_working_handler(callback: types.CallbackQuery) -> None:
    """Комманда запуска бота"""
    media_id = callback.data.split(":")[1]
    add_button_states(media_id)
    add_message_post(media_id)
    await callback.message.edit_text("🔝ㅤ", reply_markup=base_post_working_kb(media_id=media_id))

