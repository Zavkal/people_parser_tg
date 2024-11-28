import asyncio
import datetime
from zoneinfo import ZoneInfo

from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart

from bot.keyboards.start_keyboard import start_kb
from bot.middleware.check_media import check_media_post
from bot.middleware.message_type import message_media_type
from database.db import add_post_media, delete_all_post_media, add_button_states, \
    add_message_post, get_users_with_rights, get_all_post_message, del_message_post, delete_button_states, \
    delete_media_post_vk, delete_post_media_for_media_id

router = Router(name="Стартовое меню")
msk_tz = ZoneInfo("Europe/Moscow")


@router.message(CommandStart())
async def command_start_handler(message: types.Message):
    from bot.keyboards.admin_kb import start_admin_panel_kb
    await message.answer(text="Бот запущен", reply_markup=start_admin_panel_kb(message.from_user.id))
    await asyncio.sleep(2)
    await message.delete()


async def start_bot_edit_post(message: types.Message, media_id: str) -> None:
    media_group, all_message = check_media_post(media_id)  # Получаем все готовые медиа для отправки в сообщении.
    delete_all_post_media(media_id)  # Не помню для чего. Давно делал
    users = get_users_with_rights()
    mess_first_id = message.message_id
    content = all_message[0]['content']
    # Отправляем группу медиафайлов, если есть что отправить
    if media_group:
        for user in users:
            sent_messages = await message.bot.send_media_group(user[0], media=media_group)
            for msg in sent_messages:  # Получаем список message_id для каждого медиа
                if len(media_group) > 1:
                    media_id = msg.media_group_id
                else:
                    media_id = msg.message_id
                chat_id = str(msg.chat.id)
                message_id = msg.message_id
                file_id, media_type, format_file = message_media_type(msg)
                add_button_states(media_id)
                add_message_post(media_id)
                add_post_media(media_id, str(message_id), content, file_id, media_type, format_file, chat_id, str(mess_first_id))

            await message.bot.send_message(
                chat_id=user[0],  # Сюда указать айдишники всех пользвоателей через цикл отправки смс
                text="ᅠ                               🔝                       ᅠ",
                reply_markup=start_kb(media_id)
            )

    else:
        for user in users:
            sent_message = await message.bot.send_message(user[0], text=content)
            chat_id = str(sent_message.chat.id)
            message_id = sent_message.message_id
            media_id = sent_message.message_id
            file_id, media_type, format_file = message_media_type(message=sent_message)
            add_button_states(str(media_id))
            add_message_post(str(media_id))
            add_post_media(str(media_id), str(message_id), content, file_id, media_type, format_file, chat_id, str(mess_first_id))
            await message.bot.send_message(
                chat_id=user[0],
                text="ᅠ                               🔝                       ᅠ",
                reply_markup=start_kb(str(media_id))
            )

    all_bd_message = get_all_post_message()
    time_now = datetime.datetime.now(msk_tz).replace(tzinfo=None)
    for i in all_bd_message:
        media_id = i['media_id']
        time_del = datetime.datetime.strptime(i["del_time"], "%Y-%m-%d %H:%M:%S")
        if time_del < time_now:
            del_message_post(media_id)
            delete_button_states(media_id)
            delete_post_media_for_media_id(media_id)
            try:
                delete_media_post_vk(media_id)
            except Exception as e:
                pass


@router.callback_query(F.data == "close_window")
async def close_window_handler(callback: types.CallbackQuery) -> None:
    """Хендлер удаления сообщения"""
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        await callback.answer(show_alert=True, text="Сообщение устарело!\nУдалите вручную.")
