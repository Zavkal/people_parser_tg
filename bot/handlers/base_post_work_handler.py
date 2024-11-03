from aiogram import F, Router, types

from bot.keyboards.base_post_working_keyboard import base_post_working_kb
from bot.middleware.autodel_create_message import autodel_create_mg
from bot.middleware.check_media import check_media_post

router = Router(name="Начальная работа с постом")


@router.callback_query(F.data.startswith("start_working:"))
async def base_post_working_handler(callback: types.CallbackQuery) -> None:
    """Комманда запуска бота"""
    media_id = callback.data.split(":")[1]
    await callback.message.edit_text("Работа с постом", reply_markup=base_post_working_kb(media_id=media_id))

