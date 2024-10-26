from aiogram import F, Router, types

from keyboards.base_post_working_keyboard import base_post_working_kb

router = Router(name="Начальная работа с постом")


@router.callback_query(F.data == "start_working")
async def base_post_working_handler(
    callback: types.CallbackQuery,
) -> None:
    """Комманда запуска бота"""
    await callback.message.edit_reply_markup(
        reply_markup=base_post_working_kb
    )
