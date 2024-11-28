from aiogram import types


def message_media_type(message: types.Message):
    file_id, media_type, format_file = None, None, None
    if message.photo:
        file_id = message.photo[-1].file_id
        media_type = 'photos'
        format_file = '.jpg'
    elif message.video:
        file_id = message.video.file_id
        media_type = 'videos'
        format_file = '.mp4'
    elif message.document:
        file_id = message.document.file_id
        media_type = 'documents'
        format_file = '.' + message.document.file_name.split(".")[-1]
    elif message.animation:
        file_id = message.animation.file_id
        media_type = 'animations'
        format_file = '.' + message.animation.file_name.split(".")[-1]
    try:
        return file_id, media_type, format_file
    except:
        return