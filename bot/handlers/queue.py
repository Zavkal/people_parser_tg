import os
from zoneinfo import ZoneInfo

from aiogram import Router, types, flags, F
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
import datetime

from bot.middleware.check_media import check_media_post
from database.db import get_all_post_message, get_button_states

router = Router(name="Получение очереди")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

PHOTO_QUEUE_TG = FSInputFile(path=os.path.join(BASE_DIR, "img", "tg_photo.jpg"))
PHOTO_QUEUE_VK = FSInputFile(path=os.path.join(BASE_DIR, "img", "vk_photo.jpg"))

msk_tz = ZoneInfo("Europe/Moscow")


@router.message(F.text == "💎 Очередь в ТГ")
@flags.authorization(post_rights=True)
async def queue_middleware_tg(message: types.Message, ) -> None:
    await message.delete()
    await settings_parser_tg(message)


@flags.authorization(post_rights=True)
async def settings_parser_tg(message: types.Message, ) -> None:
    all_message_post = get_all_post_message()
    list_message_tg = []
    for message_post in all_message_post:
        media_id = message_post.get('media_id')
        date_tg = message_post.get('publ_time_tg')
        post = {}
        try:
            date_tg = datetime.datetime.strptime(date_tg, "%Y-%m-%d %H:%M:%S")
        except:
            date_tg = None
        if date_tg:
            time_now = datetime.datetime.now(msk_tz).replace(tzinfo=None)
            if date_tg:
                button_state = get_button_states(media_id)
                if time_now < date_tg and button_state[0] == 'on':
                    post["media_id"] = media_id
                    post["date_tg"] = date_tg
            if post:
                list_message_tg.append(post)

    inline_keyboard = []
    for post in list_message_tg:
        button = InlineKeyboardButton(
            text=f"Пост в тг {post.get('date_tg')}.",
            callback_data=f"queue_post_date:{post.get('media_id')}",
        )
        inline_keyboard.append([button])  # Каждая кнопка в отдельной строке

        # Создаем InlineKeyboardMarkup с указанием inline_keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    keyboard.inline_keyboard.extend(close_queue_post_date().inline_keyboard)

    # Редактируем сообщение с новой клавиатурой
    await message.bot.send_photo(reply_markup=keyboard,
                                 chat_id=message.chat.id,
                                 photo=PHOTO_QUEUE_TG)


@router.message(F.text == "▶️ Очередь ВК")
@flags.authorization(post_rights=True)
async def queue_middleware_vk(message: types.Message, ) -> None:
    await message.delete()
    await settings_parser_vk(message)


@flags.authorization(post_rights=True)
async def settings_parser_vk(message: types.Message, ) -> None:
    all_message_post = get_all_post_message()
    list_message_tg = []
    for message_post in all_message_post:
        media_id = message_post.get('media_id')
        date_vk = message_post.get('publ_time_vk')
        post = {}
        try:
            date_vk = datetime.datetime.strptime(date_vk, "%Y-%m-%d %H:%M:%S")
        except:
            date_vk = None
        if date_vk:
            time_now = datetime.datetime.now(msk_tz).replace(tzinfo=None)
            if date_vk:
                button_state = get_button_states(media_id)
                if time_now < date_vk and button_state[1] == 'on':
                    post["media_id"] = media_id
                    post["date_vk"] = date_vk
            if post:
                list_message_tg.append(post)
    inline_keyboard = []
    for post in list_message_tg:
        button = InlineKeyboardButton(
            text=f"Пост в вк {post.get('date_vk')}",
            callback_data=f"queue_post_date:{post.get('media_id')}",
        )
        inline_keyboard.append([button])  # Каждая кнопка в отдельной строке

        # Создаем InlineKeyboardMarkup с указанием inline_keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    keyboard.inline_keyboard.extend(close_queue_post_date().inline_keyboard)

    # Редактируем сообщение с новой клавиатурой
    await message.bot.send_photo(reply_markup=keyboard,
                                 chat_id=message.chat.id,
                                 photo=PHOTO_QUEUE_VK)


@router.callback_query(F.data.startswith("queue_post_date:"))
@flags.authorization(post_rights=True)
async def queue_post_date_mark(callback: types.CallbackQuery, ) -> None:
    media_id = callback.data.split(":")[-1]

    media_group, all_message = check_media_post(media_id)
    if media_group:
        mg_del = await callback.message.answer_media_group(media_group)
    else:
        mg_del = await callback.message.answer(all_message[0]['content'])
    if isinstance(mg_del, list):
        await callback.message.answer(text="🔝ㅤ", reply_markup=close_post(media_id=media_id, mg_del=mg_del[0].message_id))
    else:
        await callback.message.answer(text="🔝ㅤ", reply_markup=close_post(media_id=media_id, mg_del=mg_del.message_id))


@router.callback_query(F.data.startswith("delete_open_post:"))
async def queue_post_open_delete(callback: types.CallbackQuery, ) -> None:
    media_id = callback.data.split(":")[-1]
    mg_del = int(callback.data.split(":")[1])
    media_group, all_message = check_media_post(media_id)
    await callback.message.delete()
    for media in all_message:
        if media.get('file_id', None):
            try:
                await callback.bot.delete_message(callback.message.chat.id, mg_del)
            except:
                pass
        else:
            await callback.bot.delete_message(callback.message.chat.id, mg_del)
        mg_del += 1


def close_queue_post_date():
    close_queue_post_date_ = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="⛔ Закрыть", callback_data="delete_settings"),
            ]
        ]
    )
    return close_queue_post_date_


def close_post(media_id: str, mg_del: int):
    close_post_ = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="⛔ Закрыть", callback_data=f"delete_open_post:{mg_del}:{media_id}"),
            ]
        ]
    )
    return close_post_
