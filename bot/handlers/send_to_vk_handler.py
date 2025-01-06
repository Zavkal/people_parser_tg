import asyncio
import datetime
import os
import re
from zoneinfo import ZoneInfo

from aiogram import F, Router, types

from bot.keyboards.send_post_keyboard import send_post_base_kb, send_post_vk_error_kb
from bot.middleware.send_to_vk_options import get_media, upload_to_wall_vk, post_to_wall, del_media_in_folder
from database.db import update_button_states, get_post_media_by_media_id, get_all_publ_time


router = Router(name="Отправка поста в ВК")
msk_tz = ZoneInfo("Europe/Moscow")


@router.callback_query(F.data.startswith("send_to_vk:"))
async def send_to_vk_handler(callback: types.CallbackQuery, ) -> None:
    media_id = callback.data.split(':')[1]
    flag = callback.data.split(':')[-1]
    time_post = get_all_publ_time(media_id)[1]
    media_del_list = []
    update_button_states(media_id=media_id, button_vk_state='on')
    all_message = get_post_media_by_media_id(media_id)
    await callback.message.edit_reply_markup(reply_markup=send_post_base_kb(media_id))
    for msg in all_message:
        if flag != "False":
            file_type = msg['media_type']
            format_file = msg['format_file']
            file_id = msg['file_id']
            await get_media(callback=callback,
                            type_file=file_type,
                            uniq_name=file_id,
                            format_file=format_file,
                            media_id=media_id)

        else:
            try:
                file_type = msg['media_type']
                format_file = msg['format_file']
                file_id = msg['file_id']
                await get_media(callback=callback,
                                type_file=file_type,
                                uniq_name=file_id,
                                format_file=format_file,
                                media_id=media_id)
            except Exception as e:
                media_del_list.append(msg['file_id'])

    for msg in all_message:
        file_type = msg['media_type']
        format_file = msg['format_file']
        file_id = msg['file_id']
        if file_id in media_del_list:
            continue
        else:
            await upload_to_wall_vk(media_id, msg)
            await del_media_in_folder(type_file=file_type,
                                      uniq_name=file_id,
                                      format_file=format_file)

    text_message = all_message[0]["content"]
    text_without_tags = re.sub(r'<(?!a\s|/a).*?>', '', text_message)

    # Преобразуем ссылки вида <a href="URL">Текст</a> в "URL Текст"
    formatted_text = re.sub(r'<a href="(.*?)">(.*?)</a>', r'\2 - \1', text_without_tags)
    try:
        if not time_post:
            post_to_wall(media_id, formatted_text)

        else:
            time_post = datetime.datetime.strptime(time_post, "%Y-%m-%d %H:%M:%S")
            time_post = time_post.replace(tzinfo=msk_tz)

            # Преобразуем время в Unix Timestamp
            unix_timestamp = int(time_post.timestamp())
            post_to_wall(media_id, formatted_text, publish_time=unix_timestamp)

    except Exception as e:
        mess_del = await callback.bot.send_message(
            text=f"🛑Ошибка при отправлении данных, попробуйте снова. Проверьте стену ВКонтакте! Ошибка: {e}🛑",
            chat_id=callback.message.chat.id)
        await asyncio.sleep(4)
        await callback.bot.delete_message(chat_id=mess_del.chat.id,
                                          message_id=mess_del.message_id)
        update_button_states(media_id=media_id, button_vk_state='off')
        await callback.message.edit_reply_markup(reply_markup=send_post_base_kb(media_id))

    mess_del = await callback.bot.send_message(text="⚠️ Все данные успешно скачаны и загружены на сервер вконтакте для публикации.",
                                               chat_id=callback.message.chat.id)
    await asyncio.sleep(4)
    await callback.bot.delete_message(chat_id=mess_del.chat.id,
                                      message_id=mess_del.message_id)


@router.callback_query(F.data.startswith("send_to_vk_error_close:"))
async def send_to_vk_handler_error(callback: types.CallbackQuery, ) -> None:
    media_id = callback.data.split(':')[1]
    update_button_states(media_id=media_id, button_vk_state='off')
    await callback.message.edit_reply_markup(reply_markup=send_post_base_kb(media_id))




