from aiogram import types


def create_media_list(media_type: str, file_id: str, content: str = None):
    if media_type:
        if media_type == 'video':
            return types.InputMediaVideo(media=file_id, caption=content)
        elif media_type == 'photo':
            return types.InputMediaPhoto(media=file_id, caption=content)
        elif media_type == 'document':
            return types.InputMediaDocument(media=file_id, caption=content)
        elif media_type == 'animation':
            return types.InputMediaAnimation(media=file_id, caption=content)

    return None
