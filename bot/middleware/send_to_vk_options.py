import asyncio
import datetime
import logging
import os
import re

import requests
import imageio

from aiogram import types
from aiogram.client.session import aiohttp
from aiogram.exceptions import TelegramBadRequest

from telethon import TelegramClient
from telethon.sessions import StringSession

from bot.config import ADMIN
from bot.handlers.queue import msk_tz
from bot.keyboards.send_post_keyboard import send_post_vk_error_kb
from bot.service.vk_token_manager import vk_token_manager
from database.db import add_media_post_vk, get_all_post_media_vk, select_groups_vk, get_post_media_by_media_id, get_all_publ_time
from dotenv import load_dotenv

load_dotenv()

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

load_dotenv()
SESSION_USER_ID = os.getenv("SESSION_USER_ID")
STRING_SESSION = os.getenv("STRING_SESSION")
GROUP_VK_ID = int(os.getenv("GROUP_VK_ID"))


async def get_media(
        call_or_msg: types.CallbackQuery | types.Message,
        type_file: str,
        uniq_name: str,
        format_file: str,
        media_id: str,
        auto_parse: bool = False,
) -> None:
    if uniq_name:
        try:
            file_info = await call_or_msg.bot.get_file(uniq_name)
            file_path = file_info.file_path
            media_dir = os.path.join(base_dir, 'img', type_file)
            os.makedirs(media_dir, exist_ok=True)
            try:
                file_url = f"https://api.telegram.org/file/bot{call_or_msg.message.bot.token}/{file_path}"
            except Exception:
                file_url = f"https://api.telegram.org/file/bot{call_or_msg.bot.token}/{file_path}"

            destination = os.path.join(media_dir, f"{uniq_name}{format_file}")

            await download_file(file_url, destination)
        except TelegramBadRequest as e:
            try:
                if "file is too big" in str(e):
                    media_dir = os.path.join(base_dir, 'img', type_file)
                    destination = os.path.join(media_dir, f"{uniq_name}{format_file}")
                    await call_or_msg.bot.send_video(chat_id=int(SESSION_USER_ID),
                                                     video=uniq_name,
                                                     caption=f"{media_id},{uniq_name}")

                    await download_big_file(media_id, destination, STRING_SESSION)
            except Exception as e:
                if not auto_parse:
                    mess_del = await call_or_msg.bot.send_message(
                        text=f"🛑СЕССИЯ МЕРТВА🛑",
                        chat_id=call_or_msg.message.chat.id)
                    await asyncio.sleep(4)
                    await call_or_msg.bot.delete_message(chat_id=mess_del.chat.id,
                                                         message_id=mess_del.message_id)
                    await call_or_msg.message.edit_reply_markup(
                        reply_markup=send_post_vk_error_kb(media_id, flag=False))
                else:
                    await call_or_msg.bot.send_message(chat_id=ADMIN,
                                                       text="🛑СЕССИЯ МЕРТВА🛑")

        except Exception as e:
            if not auto_parse:
                mess_del = await call_or_msg.bot.send_message(
                    text=f"🛑Не смог скачать 1 файл. Ошибка:\n {e}🛑",
                    chat_id=call_or_msg.message.chat.id)
                await asyncio.sleep(4)
                await call_or_msg.bot.delete_message(chat_id=mess_del.chat.id,
                                                     message_id=mess_del.message_id)
                await call_or_msg.message.edit_reply_markup(reply_markup=send_post_vk_error_kb(media_id, flag=False))
                return

            else:
                await call_or_msg.bot.send_message(chat_id=ADMIN,
                                                   text=f"🛑Не смог скачать 1 файл для авто-поста в вк. Ошибка:\n {e}🛑")
                return


async def download_file(file_url, destination):
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            if response.status == 200:
                with open(destination, 'wb') as f:
                    f.write(await response.read())


async def upload_to_wall_vk(
        media_id: str,
        msg: dict,
) -> None:
    await vk_token_manager.ensure_access_token_async()
    vk = vk_token_manager.get_api()

    if msg['media_type']:
        media_dir = os.path.join(base_dir, 'img', msg['media_type'])

    # 1. Получение URL сервера для загрузки изображений
    if msg['media_type'] == 'photos':
        upload_server = vk.photos.getWallUploadServer(group_id=GROUP_VK_ID)
        upload_url = upload_server.get('upload_url')

        file_path = os.path.join(media_dir, f"{msg['file_id']}{msg['format_file']}")
        with open(file_path, 'rb') as file:
            response = requests.post(upload_url, files={'photo': file})

            try:
                response_json = response.json()
            except Exception as e:
                logging.error("Ошибка при разборе JSON:", e)
                return None

        # 3. Сохранение изображения в альбом группы
        saved = vk.photos.saveWallPhoto(
            group_id=GROUP_VK_ID,
            photo=response_json['photo'],
            server=response_json['server'],
            hash=response_json['hash']
        )[0]

        add_media_post_vk(media_id, f"photo{saved['owner_id']}_{saved['id']}")

    elif msg["media_type"] == 'videos':
        all_post_msg = get_post_media_by_media_id(media_id)
        text_message = all_post_msg[0]["content"]
        text_without_tags = re.sub(r'<(?!a\s|/a).*?>', '', text_message)

        # Преобразуем ссылки вида <a href="URL">Текст</a> в "URL Текст"
        formatted_text = re.sub(r'<a href="(.*?)">(.*?)</a>', r'\2 - \1', text_without_tags)
        upload_url = vk.video.save(
            group_id=GROUP_VK_ID,
            name="💎 XboxRent",
            description=formatted_text
        )['upload_url']

        file_path = os.path.join(media_dir, f"{msg['file_id']}{msg['format_file']}")
        with open(file_path, 'rb') as file:
            response = requests.post(upload_url, files={'video_file': file}).json()

        video = response.get('video_id')
        owner_id = response.get('owner_id')
        add_media_post_vk(media_id, f"video{owner_id}_{video}")

    elif msg['media_type'] == 'documents' and msg['format_file'] == '.mp4':
        upload_server = vk.docs.getWallUploadServer(group_id=GROUP_VK_ID)
        upload_url = upload_server['upload_url']

        old_file_path = os.path.join(media_dir, f"{msg['file_id']}{msg['format_file']}")
        new_file_path = old_file_path.replace('.mp4', '.gif')
        mp4_to_gif(old_file_path, new_file_path)
        with open(new_file_path, 'rb') as file:
            response = requests.post(upload_url, files={'file': file}).json()

        # Сохраняем документ
        file_id = response['file']

        # Сохранение документа
        doc = vk.docs.save(file=file_id)
        doc_id = doc['doc']['id']
        owner_id = doc['doc']['owner_id']

        # Прикрепление документа к посту
        add_media_post_vk(media_id, f"doc{owner_id}_{doc_id}")


def mp4_to_gif(input_mp4_path, output_gif_path):
    reader = imageio.get_reader(input_mp4_path)
    fps = reader.get_meta_data()['fps']  # Получаем FPS из метаданных
    writer = imageio.get_writer(output_gif_path, fps=fps)

    for frame in reader:
        writer.append_data(frame)
    writer.close()


async def post_to_wall_vk(
        media_id: str,
        call_or_msg: types.CallbackQuery | types.Message,
) -> None:
    await vk_token_manager.ensure_access_token_async()

    formatted_text = await aggregate_post_and_download_media(
        media_id=media_id,
        call_or_msg=call_or_msg,
    )

    time_post = get_all_publ_time(media_id)[1]

    if time_post:
        time_post = datetime.datetime.strptime(time_post, "%Y-%m-%d %H:%M:%S")
        time_post = time_post.replace(tzinfo=msk_tz)

        # Преобразуем время в Unix Timestamp
        publish_time = int(time_post.timestamp())
    else:
        publish_time = None

    media = get_all_post_media_vk(media_id)
    attachments = ""

    for media_vk_id in media:
        attachments += "," + media_vk_id['media']

    vk = vk_token_manager.get_api()
    groups = select_groups_vk()
    for group in groups:
        vk.wall.post(
            owner_id=int(group[1]),  # Отрицательный ID группы
            from_group=1,
            message=formatted_text,
            attachments=attachments,
            publish_date=publish_time,
        )


async def del_media_in_folder(type_file: str, uniq_name: str, format_file: str):
    if uniq_name:
        media_dir = os.path.join(base_dir, 'img', type_file)
        destination = os.path.join(media_dir, f"{uniq_name}{format_file}")
        os.remove(destination)


async def download_big_file(media_id: str, destination: str, STRING_SESSION: str):
    json_data = {
        "app_id": 2040,
        "app_hash": "b18441a1ff607e10a989891a5462e627",
        "sdk": "Windows 10",
        "app_version": "5.1.7 x64",
        "device": "Desktop",
        "system_lang_pack": "en-US",
        "lang_pack": "tdesktop", }

    client = TelegramClient(StringSession(STRING_SESSION),
                            api_id=json_data['app_id'],
                            api_hash=json_data['app_hash'],
                            app_version=json_data['app_version'],
                            device_model=json_data['device'],
                            system_lang_code=json_data["system_lang_pack"])

    await client.connect()
    if not await client.is_user_authorized():
        raise Exception
    else:
        # await client.send_message("@sdfsdfsfdfdsd_test_temp_bot", message="/start") $@x_pars_news_bot
        messages = await client.get_messages("@x_pars_news_bot", limit=10)
        for msg in messages:
            if media_id in msg.text:
                await client.download_media(msg, file=destination)


async def aggregate_post_and_download_media(
        media_id: str,
        call_or_msg: types.Message | types.CallbackQuery,
) -> str:
    all_message = get_post_media_by_media_id(media_id)

    media_del_list = []

    for msg in all_message:
        try:
            file_type = msg['media_type']
            format_file = msg['format_file']
            file_id = msg['file_id']
            await get_media(
                call_or_msg=call_or_msg,
                type_file=file_type,
                uniq_name=file_id,
                format_file=format_file,
                media_id=media_id,
            )
        except Exception as e:
            media_del_list.append(msg['file_id'])

    for msg in all_message:
        file_type = msg['media_type']
        format_file = msg['format_file']
        file_id = msg['file_id']
        if file_id in media_del_list:
            await del_media_in_folder(type_file=file_type,
                                      uniq_name=file_id,
                                      format_file=format_file)
        else:
            await upload_to_wall_vk(media_id, msg)
            await del_media_in_folder(type_file=file_type,
                                      uniq_name=file_id,
                                      format_file=format_file)

    text_message = all_message[0]["content"]
    text_without_tags = re.sub(r'<(?!a\s|/a).*?>', '', text_message)

    # Преобразуем ссылки вида <a href="URL">Текст</a> в "URL Текст"
    formatted_text = re.sub(r'<a href="(.*?)">(.*?)</a>', r'\2 - \1', text_without_tags)

    return formatted_text
