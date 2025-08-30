import asyncio
import datetime
from zoneinfo import ZoneInfo

from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart

from bot.config import uniq_text_auto_pars, ADMIN
from bot.keyboards.start_keyboard import start_kb
from bot.middleware.check_media import check_media_post
from bot.middleware.message_type import message_media_type
from bot.middleware.send_to_vk_options import post_to_wall_vk
from bot.service.post_to_tg_service import state_time_publish_post
from bot.service.search_uniq_text import search_and_replace
from database.db import add_post_media, delete_all_post_media, add_button_states, \
    add_message_post, get_users_with_rights, get_all_post_message, del_message_post, delete_button_states, \
    delete_media_post_vk, delete_post_media_for_media_id, get_post_media_by_media_id

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
    mess_text_for_auto_pars = all_message[0]['content']
    # Отправляем группу медиафайлов, если есть что отправить
    if media_group:
        for user in users:
            counter = 1
            if search_and_replace(content=mess_text_for_auto_pars, replace=True):
                content = all_message[0]['content']
            else:
                content = all_message[0]['content']

            sent_messages = await message.bot.send_media_group(user[0], media=media_group)
            for msg in sent_messages:  # Получаем список message_id для каждого медиа
                if len(media_group) > 1:
                    media_id = msg.media_group_id
                else:
                    media_id = msg.message_id
                if counter != 1:
                    content = ''
                chat_id = str(msg.chat.id)
                message_id = msg.message_id
                file_id, media_type, format_file = message_media_type(msg)
                add_button_states(media_id)
                add_message_post(media_id)
                add_post_media(media_id, str(message_id), content, file_id, media_type, format_file, chat_id,
                               str(mess_first_id))
                counter -= 1
            if search_and_replace(content=mess_text_for_auto_pars):
                await message.bot.send_message(
                    chat_id=user[0],  # Сюда указать айдишники всех пользвоателей через цикл отправки смс
                    text=f"Пост был автоматически отправлен во все сервисы, клавиатуру не вызываю.\n media_id={media_id}"
                )
            else:
                await message.bot.send_message(
                    chat_id=user[0],  # Сюда указать айдишники всех пользвоателей через цикл отправки смс
                    text="ᅠ                               🔝                       ᅠ",
                    reply_markup=start_kb(media_id)
                )

    else:
        for user in users:
            if search_and_replace(content=mess_text_for_auto_pars, replace=True):
                content = all_message[0]['content']
            else:
                content = all_message[0]['content']
            sent_message = await message.bot.send_message(user[0], text=content)
            chat_id = str(sent_message.chat.id)
            message_id = sent_message.message_id
            media_id = sent_message.message_id
            file_id, media_type, format_file = message_media_type(message=sent_message)
            add_button_states(str(media_id))
            add_message_post(str(media_id))
            add_post_media(str(media_id), str(message_id), content, file_id, media_type, format_file, chat_id,
                           str(mess_first_id))
            if search_and_replace(content=mess_text_for_auto_pars):
                await message.bot.send_message(
                    chat_id=user[0],  # Сюда указать айдишники всех пользвоателей через цикл отправки смс
                    text=f"Пост был автоматически отправлен во все сервисы, клавиатуру не вызываю.\n media_id={media_id}"
                )
            else:
                await message.bot.send_message(
                    chat_id=user[0],
                    text="ᅠ                               🔝                       ᅠ",
                    reply_markup=start_kb(str(media_id))
                )
    if search_and_replace(content=mess_text_for_auto_pars):
        # Авто-отправка поста в тг
        try:
            await state_time_publish_post(
                media_id=media_id,
                time_sleep=1,
                call_or_msg=message
            )
        except Exception as exc:
            await message.bot.send_message(
                text=f"Ошибка при авто-отправке поста в тг \n{exc}\n\nmedia_id={media_id}",
                chat_id=int(ADMIN)
            )

        # Авто-отправка поста в вк
        try:
            await post_to_wall_vk(
            media_id=media_id,
            call_or_msg=message,)

        except Exception as exc:
            await message.bot.send_message(
                text=f"Ошибка при авто-отправке поста в вк \n{exc}\n\nmedia_id={media_id}",
                chat_id=int(ADMIN)
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


@router.callback_query(F.data.startswith("close_window:"))
async def close_window_handler(callback: types.CallbackQuery) -> None:
    media_id = callback.data.split(":")[1]
    msg_del = []
    all_message = get_post_media_by_media_id(media_id)
    for msg in all_message:
        msg_del.append(int(msg.get("message_id")))
    await callback.bot.delete_messages(chat_id=callback.message.chat.id,
                                       message_ids=msg_del)
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        await callback.answer(show_alert=True, text="Сообщение устарело!\nУдалите вручную.")
