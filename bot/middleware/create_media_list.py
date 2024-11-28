from aiogram import types


def create_media_list(media_type: str, file_id: str, content: str = None):
    if media_type:
        if media_type == 'videos':
            return types.InputMediaVideo(media=file_id, caption=content)
        elif media_type == 'photos':
            return types.InputMediaPhoto(media=file_id, caption=content)
        elif media_type == 'documents':
            return types.InputMediaDocument(media=file_id, caption=content)
        elif media_type == 'animations':
            return types.InputMediaAnimation(media=file_id, caption=content)

    return None
