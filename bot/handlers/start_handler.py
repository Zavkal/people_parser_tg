from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart

from keyboards.start_keyboard import start_kb

router = Router(name="Стартовое меню")


@router.message(CommandStart())
async def command_start_handler(
    message: types.Message,
) -> None:
    """Комманда запуска бота"""
    await message.bot.send_message(
        chat_id=message.from_user.id,
        text="Какой то пост",
        reply_markup=start_kb
    )


@router.callback_query(F.data == "close_window")
async def close_window_handler(callback: types.CallbackQuery) -> None:
    """Хендлер удаления сообщения"""
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        await callback.answer(show_alert=True, text="Сообщение устарело!\nУдалите вручную.")
