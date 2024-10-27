from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart


from bot.keyboards.start_keyboard import start_kb
from database.db import get_post_media_by_media_id

router = Router(name="Стартовое меню")


@router.message(CommandStart())
async def command_start_handler(message: types.Message, media_id: str) -> None:
    all_message = get_post_media_by_media_id(media_id)
    media_group = []

    # Перебираем все записи и проверяем тип файла
    for record in all_message:
        file_id = record['file_id']
        media_type = record['media_type']
    if media_type:
        if media_type == 'video':
            # Если тип 'video', добавляем как InputMediaVideo
            media_group.append(types.InputMediaVideo(media=file_id))
        elif media_type == 'photo':
            # Если тип 'photo', добавляем как InputMediaPhoto
            media_group.append(types.InputMediaPhoto(media=file_id))
        elif media_type == 'document':
            media_group.append(types.InputMediaDocument(media=file_id))
        elif media_type == 'animation':
            media_group.append(types.InputMediaAnimation(media=file_id))

        await message.bot.send_media_group(message.from_user.id, media=media_group)
    if content := all_message[0]['content']:
        await message.bot.send_message(
            chat_id=message.from_user.id,
            text=content,
            reply_markup=start_kb)


@router.callback_query(F.data == "close_window")
async def close_window_handler(callback: types.CallbackQuery) -> None:
    """Хендлер удаления сообщения"""
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        await callback.answer(show_alert=True, text="Сообщение устарело!\nУдалите вручную.")
