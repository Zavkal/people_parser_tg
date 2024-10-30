from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart


from bot.keyboards.start_keyboard import start_kb
from bot.middleware.check_media import check_media_post
from database.db import get_post_media_by_media_id

router = Router(name="Стартовое меню")


@router.message(CommandStart())
async def command_start_handler(message: types.Message, media_id: str) -> None:
    media_group, all_message = check_media_post(media_id)  # --> Получаем все готовые медиа для отправки в сообщении.

    # Отправляем группу медиафайлов, если есть что отправить
    if media_group:
        await message.bot.send_media_group(message.from_user.id, media=media_group)
    else:
        await message.bot.send_message(message.from_user.id, text=message.text)

    await message.bot.send_message(
        chat_id=message.from_user.id,
        text="Начало работы.",
        reply_markup=start_kb(media_id)
    )


@router.callback_query(F.data == "close_window")
async def close_window_handler(callback: types.CallbackQuery) -> None:
    """Хендлер удаления сообщения"""
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        await callback.answer(show_alert=True, text="Сообщение устарело!\nУдалите вручную.")
