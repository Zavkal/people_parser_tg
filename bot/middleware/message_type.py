from aiogram import types


def message_media_type(message: types.Message):
    file_id, media_type, format_file = None, None, None
    if message.photo:
        file_id = message.photo[-1].file_id
        media_type = 'photo'
        format_file = '.jpg'
    elif message.video:
        file_id = message.video.file_id
        media_type = 'video'
        format_file = '.mp4'
    elif message.document:
        file_id = message.document.file_id
        media_type = 'document'
        format_file = message.document.file_name
    elif message.animation:
        file_id = message.animation.file_id
        media_type = 'animation'
        format_file = message.animation.file_name
    try:
        return file_id, media_type, format_file
    except:
        return