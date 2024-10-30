from bot.middleware.create_media_list import create_media_list
from database.db import get_post_media_by_media_id


def check_media_post(media_id: str):
    media_group = []
    all_message = get_post_media_by_media_id(media_id)
    # Перебираем все записи и проверяем тип файла
    for record in all_message:
        file_id = record['file_id']
        media_type = record['media_type']
        content = record.get('content', None)
        if media_type:  # Проверяем, что это сообщение media
            media_item = create_media_list(media_type, file_id, content)

            if media_item:  # Проверяем, что медиа-объект валиден
                media_group.append(media_item)

    return media_group, all_message
