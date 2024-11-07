from aiogram import types


#  Для callback
async def autodel_create_mg(callback: types.CallbackQuery, all_message: list, media_group: list):
    await callback.message.delete()
    counter = callback.message.message_id
    for media in all_message:
        counter -= 1
        if media.get('file_id', None):
            try:
                await callback.bot.delete_message(int(all_message[0]['user_id']), counter)
            except:
                pass

    if media_group:
        await callback.message.answer_media_group(media_group)
    else:
        try:
            await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id - 1)
        except:
            pass
        await callback.message.answer(all_message[0]['content'])


#  Для message
async def autodel_create_mg_(message: types.Message, all_message: list, media_group: list, prompt_message_id: int):
    await message.delete()
    for media in all_message:
        prompt_message_id -= 1
        if media.get('file_id', None):
            try:
                await message.bot.delete_message(message.chat.id, prompt_message_id)
            except:
                pass

    if media_group:
        await message.answer_media_group(media_group)
    else:
        try:
            await message.bot.delete_message(chat_id=message.chat.id,
                                             message_id=prompt_message_id -1)
        except:
            pass
        await message.answer(all_message[0]['content'])




