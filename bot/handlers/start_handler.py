from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart


from bot.keyboards.start_keyboard import start_kb
from bot.middleware.check_media import check_media_post
from bot.middleware.message_type import message_media_type
from database.db import get_post_media_by_media_id, add_post_media, delete_all_post_media

router = Router(name="Стартовое меню")


@router.message(CommandStart())
async def command_start_handler(message: types.Message, media_id: str) -> None:
    media_group, all_message = check_media_post(media_id)  # Получаем все готовые медиа для отправки в сообщении.
    delete_all_post_media(media_id)
    # Отправляем группу медиафайлов, если есть что отправить
    if media_group:
        sent_messages = await message.bot.send_media_group(message.from_user.id, media=media_group)
        for msg in sent_messages:  # Получаем список message_id для каждого медиа
            if len(media_group) > 1:
                media_id = msg.media_group_id
            else:
                media_id = msg.message_id
            chat_id = str(msg.chat.id)
            message_id = msg.message_id
            content = msg.caption or msg.text or ''
            file_id, media_type, format_file = message_media_type(msg)

            add_post_media(media_id, message_id, content, file_id, media_type, format_file, chat_id)
    else:
        sent_message = await message.bot.send_message(message.from_user.id, text=message.text)
        chat_id = str(sent_message.chat.id)
        message_id = sent_message.message_id
        media_id = sent_message.message_id
        content = sent_message.text or sent_message.caption or ''
        file_id, media_type, format_file = message_media_type(message=sent_message)
        add_post_media(media_id, message_id, content, file_id, media_type, format_file, chat_id)


    # Отправляем сообщение с началом работы
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
