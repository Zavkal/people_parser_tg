import os

import requests
import vk_api
import imageio

from aiogram import types
from aiogram.client.session import aiohttp
from dotenv import load_dotenv

from database.db import add_media_post_vk, get_all_post_media_vk, select_groups_vk

load_dotenv()

vk_token = os.getenv("VK_USER_TOKEN")
# Создание сессии API ВКонтакте с использованием токена группы
vk_session = vk_api.VkApi(token=vk_token)
vk = vk_session.get_api()


async def get_media(callback: types.CallbackQuery, type_file: str, uniq_name: str, format_file: str):
    if uniq_name:
        file_info = await callback.bot.get_file(uniq_name)
        file_path = file_info.file_path
        os.makedirs(f'../img/{type_file}', exist_ok=True)
        file_url = f"http://127.0.0.1:8081/bot{callback.message.bot.token}/{file_path}"
        destination = f"../img/{type_file}/{uniq_name}{format_file}"
        await download_file(file_url, destination)


async def download_file(file_url, destination):
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            if response.status == 200:
                with open(destination, 'wb') as f:
                    f.write(await response.read())


async def upload_to_wall_vk(media_id: str, msg: dict):
    # 1. Получение URL сервера для загрузки изображений
    if msg['media_type'] == 'photos':
        upload_server = vk.photos.getWallUploadServer(group_id=227946323)
        upload_url = upload_server.get('upload_url')

        # 2. Загрузка изображения на сервер
        with open('../img/' + msg['media_type'] + '/' + msg['file_id'] + msg['format_file'], 'rb') as file:
            response = requests.post(upload_url, files={'photo': file})

            try:
                response_json = response.json()
            except Exception as e:
                print("Ошибка при разборе JSON:", e)
                print(response.content)
                return None

        # 3. Сохранение изображения в альбом группы
        saved = vk.photos.saveWallPhoto(
            group_id=227946323,
            photo=response_json['photo'],
            server=response_json['server'],
            hash=response_json['hash']
        )[0]

        add_media_post_vk(media_id, f"photo{saved['owner_id']}_{saved['id']}")

    elif msg["media_type"] == 'videos':
        upload_url = vk.video.save(
            group_id=227946323,
            name=msg.get('message_id'),
            description=msg.get('file_id')
        )['upload_url']
        print(upload_url)

        with open('../img/' + msg['media_type'] + '/' + msg['file_id'] + msg['format_file'], 'rb') as file:
            response = requests.post(upload_url, files={'video_file': file}).json()

        video = response.get('video_id')
        owner_id = response.get('owner_id')
        add_media_post_vk(media_id, f"video{owner_id}_{video}")

    elif msg['media_type'] == 'documents' and msg['format_file'] == '.mp4':
        upload_server = vk.docs.getWallUploadServer(group_id=227946323)
        upload_url = upload_server['upload_url']

        old_file_path = '../img/' + msg['media_type'] + '/' + msg['file_id'] + msg['format_file']
        new_file_path = old_file_path.replace('.mp4', '.gif')
        mp4_to_gif(old_file_path, new_file_path)
        with open(new_file_path, 'rb') as file:
            response = requests.post(upload_url, files={'file': file}).json()

        print(response)
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


def post_to_wall(media_id: str, message: str, publish_time: int = None):
    media = get_all_post_media_vk(media_id)
    attachments = ""
    for media_vk_id in media:
        attachments += "," + media_vk_id['media']

    groups = select_groups_vk()
    for group in groups:
        vk.wall.post(
            owner_id=int(group[1]),  # Отрицательный ID группы
            from_group=1,
            message=message,
            attachments=attachments,
            publish_date=publish_time,
        )


async def del_media_in_folder(type_file: str, uniq_name: str, format_file: str):
    if uniq_name:
        destination = f"../img/{type_file}/{uniq_name}{format_file}"
        os.remove(destination)
