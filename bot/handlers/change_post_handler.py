import re

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.handlers.pars_message_chat import message_media_type
from bot.keyboards.base_post_working_keyboard import base_post_working_kb
from bot.keyboards.change_post_keyboard import (
    change_description_kb,
    change_media_kb,
    change_post_kb, change_text_kb, back_to_change_description_kb, back_button_change_media,
    back_button_change_text, settings_description_kb, edit_signature_kb
)

from bot.middleware.check_media import check_media_post
from bot.middleware.create_media_list import create_media_list
from database.db import get_all_signatures, add_signature, delete_signature, get_signature_by_id, \
    get_post_media_by_media_id, add_post_media, update_post_media_entry, \
    delete_post_media_entry, update_file_id, update_first_media_content, delete_all_post_media, update_signature, \
    update_flag_signature, add_button_states, delete_button_states, add_message_post, del_message_post

router = Router(name="Изменение поста")


class TextStates(StatesGroup):
    waiting_for_new_signature = State()
    waiting_for_new_text = State()
    waiting_for_replace_signature = State()


class MediaState(StatesGroup):
    waiting_for_media = State()
    waiting_for_media_number = State()
    waiting_for_media_change = State()


@router.callback_query(F.data.startswith("change_post:"))
async def change_post_handler(
        callback: types.CallbackQuery
) -> None:
    media_id = callback.data.split(":")[1]
    await callback.message.edit_text(text="ᅠ                               🔝                       ᅠ",
                                     reply_markup=change_post_kb(media_id=media_id))


# ====================================DESCRIPTION====================================================
@router.callback_query(F.data.startswith("change_description:"))
async def change_description_handler(callback: types.CallbackQuery) -> None:
    media_id = callback.data.split(":")[1]
    signatures = get_all_signatures()  # Получаем все подписи
    inline_keyboard = []  # Создаем список для кнопок
    if signatures:
        for signature in signatures:
            title = signature.get('title', None)
            if title:
                title = re.sub('<.*?>', '', title)
                button = InlineKeyboardButton(
                    text=title,
                    callback_data=f"signature:{signature['id']}:{media_id}",
                )
                inline_keyboard.append([button])  # Каждая кнопка в отдельной строке

    # Создаем InlineKeyboardMarkup с указанием inline_keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    # Объединяем обе клавиатуры
    keyboard.inline_keyboard.extend(settings_description_kb(media_id).inline_keyboard)

    # Редактируем сообщение с новой клавиатурой
    await callback.message.edit_text("ᅠ                               🔝                       ᅠ", reply_markup=keyboard,
                                     parse_mode="html")


@router.callback_query(F.data.startswith("signature:"))
async def handle_signature_selection(callback: types.CallbackQuery) -> None:
    signature_id = callback.data.split(":")[1]  # Получаем ID подписи
    media_id = callback.data.split(":")[-1]
    signature = get_signature_by_id(signature_id)  # Получаем подпись по ID из БД
    if signature:
        new_signature_text = f"\n\n{signature['title']}"  # Подготавливаем новый текст
        if get_post_media_by_media_id(media_id=media_id)[0]['content']:
            new_content = get_post_media_by_media_id(media_id=media_id)[0]['content'] + new_signature_text
            update_first_media_content(media_id, new_content)
        else:
            update_first_media_content(media_id, new_signature_text)
        first_message = get_post_media_by_media_id(media_id)[0]

        update_flag_signature(media_id, first_message['flag'] + 1)
        if first_message['file_id']:
            await callback.bot.edit_message_caption(message_id=first_message['message_id'],
                                                    caption=first_message['content'],
                                                    chat_id=first_message['chat_id'])
        else:
            await callback.bot.edit_message_text(message_id=first_message['message_id'],
                                                 text=first_message['content'],
                                                 chat_id=first_message['chat_id'])

    await callback.message.edit_reply_markup(reply_markup=base_post_working_kb(media_id))


@router.callback_query(F.data.startswith("settings_description:"))
async def add_description_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    media_id = callback.data.split(":")[1]
    signatures = get_all_signatures()  # Получаем все подписи
    inline_keyboard = []  # Создаем список для кнопок
    if signatures:
        for signature in signatures:
            title = signature.get('title', None)
            if title:
                title = re.sub('<.*?>', '', title)
                button = InlineKeyboardButton(
                    text=title,
                    callback_data=f"change_signature:{signature['id']}:{media_id}"
                    # Уникальный callback_data для каждой кнопки
                )
                inline_keyboard.append([button])  # Каждая кнопка в отдельной строке

    # Создаем InlineKeyboardMarkup с указанием inline_keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    # Объединяем обе клавиатуры
    keyboard.inline_keyboard.extend(change_description_kb(media_id).inline_keyboard)
    await callback.message.edit_text(
        text="ᅠ                            🔝                       ᅠ\nᅠ                 Настройки подписи",
        reply_markup=keyboard)


@router.callback_query(F.data.startswith("change_signature:"))
async def add_description_handler(callback: types.CallbackQuery) -> None:
    signature_id = callback.data.split(":")[1]  # Получаем ID подписи
    media_id = callback.data.split(":")[-1]
    await callback.message.edit_text(get_signature_by_id(signature_id)['title'],
                                     reply_markup=edit_signature_kb(media_id, signature_id))


@router.callback_query(F.data.startswith("edit_signature:"))
async def add_description_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    signature_id = callback.data.split(":")[1]  # Получаем ID подписи
    media_id = callback.data.split(":")[-1]
    message_kb = callback.message.message_id
    chat_id = callback.message.chat.id
    await state.update_data(signature_id=signature_id,
                            message_kb=message_kb,
                            chat_id=chat_id,
                            media_id=media_id)
    await callback.answer("Введите подпись")
    # Сохраняем состояние для ожидания текста
    await state.set_state(TextStates.waiting_for_replace_signature)


@router.message(TextStates.waiting_for_replace_signature)
async def handle_new_signature(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    media_id = data.get('media_id')
    signature_id = data.get('signature_id')
    message_kb = data.get('message_kb')
    chat_id = data.get('chat_id')

    new_description = message.html_text
    await message.delete()
    # Сохранение новой подписи в БД
    update_signature(signature_id, new_description)
    await message.bot.edit_message_text(text=new_description,
                                        chat_id=chat_id,
                                        message_id=message_kb,
                                        reply_markup=edit_signature_kb(media_id, signature_id)
                                        )

    # Сбрасываем состояние
    await state.clear()


@router.callback_query(F.data.startswith("add_description:"))
async def add_description_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    # Показываем только кнопку "Назад"
    media_id = callback.data.split(":")[1]
    await state.update_data(media_id=media_id, inline_message_id=callback.message.message_id)

    # Подтверждаем нажатие кнопки и отправляем клавиатуру
    await callback.answer("Введите подпись")
    await callback.message.edit_reply_markup(reply_markup=back_to_change_description_kb(media_id))

    # Сохраняем состояние для ожидания текста
    await state.set_state(TextStates.waiting_for_new_signature)


@router.message(TextStates.waiting_for_new_signature)
async def handle_new_signature(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    media_id = data.get('media_id')
    inline_message_id = data.get('inline_message_id')
    new_description = message.html_text
    await message.delete()
    # Сохранение новой подписи в БД
    add_signature(new_description)

    # Получаем все подписи и создаем новую клавиатуру с подписями
    signatures = get_all_signatures()
    inline_keyboard = []

    # Проверяем, есть ли подписи, и добавляем их в клавиатуру
    if signatures:
        for signature in signatures:
            title = signature.get('title')  # Получаем заголовок подписи
            if title:  # Проверяем, что title не None или пустая строка
                title = re.sub('<.*?>', '', title)
                button = InlineKeyboardButton(
                    text=title,
                    callback_data=f"signature:{signature['id']}:{media_id}"
                    # Уникальный callback_data для каждой кнопки
                )
                inline_keyboard.append([button])  # Каждая кнопка в отдельной строке

    # Создаем InlineKeyboardMarkup с кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    keyboard.inline_keyboard.extend(settings_description_kb(media_id).inline_keyboard)  # Объединяем клавиатуры

    # Отправляем клавиатуру без изменения текста сообщения
    await message.bot.edit_message_reply_markup(
        chat_id=message.chat.id,
        message_id=inline_message_id,
        reply_markup=keyboard
    )

    # Сбрасываем состояние
    await state.clear()


@router.callback_query(F.data.startswith("remove_description:"))
async def remove_signature_handler(callback: types.CallbackQuery) -> None:
    media_id = callback.data.split(":")[1]
    signatures = get_all_signatures()

    if signatures:
        # Создаем клавиатуру с оставшимися подписями
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=f"Удалить:  {signature['title']}",
                callback_data=f"remove_signature:{signature['id']}:{media_id}"
            )] for signature in signatures
        ])

        # Добавляем кнопку "Назад"
        keyboard.inline_keyboard.extend(back_to_change_description_kb(media_id).inline_keyboard)

        # Обновляем сообщение с новой клавиатурой
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    else:
        await callback.message.edit_reply_markup(reply_markup=back_to_change_description_kb(media_id))

    await callback.answer()


@router.callback_query(F.data.startswith("remove_signature:"))
async def remove_signature_handler(callback: types.CallbackQuery) -> None:
    signature_id = callback.data.split(":")[1]
    media_id = callback.data.split(":")[-1]

    delete_signature(int(signature_id))  # Удаляем подпись из базы данных

    signatures = get_all_signatures()  # Получаем обновленный список подписей

    # Проверка на наличие оставшихся подписей
    if signatures:
        # Создаем клавиатуру с кнопками оставшихся подписей
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Удалить: {signature['title']}",
                    callback_data=f"remove_signature:{signature['id']}:{media_id}"
                )
            ] for signature in signatures
        ])

        # Добавляем кнопку "Назад" как отдельную строку
        keyboard.inline_keyboard.extend(back_to_change_description_kb(media_id).inline_keyboard)

        # Обновляем сообщение с новой клавиатурой
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    else:
        # Если подписей больше нет, показываем только кнопку "Назад"
        await callback.message.edit_reply_markup(reply_markup=back_to_change_description_kb(media_id))

    await callback.answer("Подпись удалена.")  # Подтверждаем удаление


@router.callback_query(F.data.startswith("del_add_signature_text:"))
async def del_text_signature_handler(callback: types.CallbackQuery) -> None:
    media_id = callback.data.split(":")[1]
    all_message = get_post_media_by_media_id(media_id)
    update_flag_signature(media_id, flag=all_message[0]['flag'] - 1)
    media_group, all_message = check_media_post(media_id)
    chat_id = all_message[0]['chat_id']
    caption = all_message[0]['content']
    message_id = all_message[0]['message_id']
    signatures = get_all_signatures()
    index_list = []
    for sign in signatures:
        if sign['title'] in caption:
            index_cap = caption.rfind(sign['title'])
            index_list.append({"value": index_cap, index_cap: sign['title']})
    max_dict = max(index_list, key=lambda x: x["value"])
    max_dict = max_dict.get('value') - 2
    caption = caption[:max_dict]

    update_first_media_content(media_id, caption)

    if media_group:
        await callback.bot.edit_message_caption(chat_id=chat_id,
                                                message_id=message_id,
                                                caption=caption)
    else:
        await callback.bot.edit_message_text(chat_id=chat_id,
                                             message_id=message_id,
                                             text=caption)

    signatures = get_all_signatures()
    inline_keyboard = []
    if signatures:
        for signature in signatures:
            title = signature.get('title', None)
            if title:
                title = re.sub('<.*?>', '', title)
                button = InlineKeyboardButton(
                    text=title,
                    callback_data=f"signature:{signature['id']}:{media_id}"
                )
                inline_keyboard.append([button])

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    keyboard.inline_keyboard.extend(settings_description_kb(media_id).inline_keyboard)

    if all_message[0]['flag'] == 0:
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    else:
        await callback.answer("Вы удалили подпись")


# ====================================MEDIA====================================================
@router.callback_query(F.data.startswith("change_media:"))
async def change_media_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    media_id = callback.data.split(":")[1]
    # Отправляем текстовое сообщение, если контент существует

    await callback.message.edit_text(
        text="ᅠ                               🔝                       ᅠ",
        reply_markup=change_media_kb(media_id))


#  Кнопка Добавить медиа
@router.callback_query(F.data.startswith("add_media_post:"))
async def add_media_post(callback: types.CallbackQuery, state: FSMContext) -> None:
    media_id = callback.data.split(":")[1]
    await callback.answer("Отправьте медиа для добавления.")
    message_kb_del = await callback.message.edit_reply_markup(reply_markup=back_button_change_media(media_id))
    await state.update_data(media_id=media_id,
                            prompt_message_id=callback.message.message_id,
                            message_kb_del=message_kb_del.message_id)
    await state.set_state(MediaState.waiting_for_media)


@router.message(MediaState.waiting_for_media)
async def handle_media_input(message: types.Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    media_id = user_data["media_id"]
    # Получаем id сообщения из состояния для удаления.
    prompt_message_id = user_data["prompt_message_id"]
    message_kb_del = user_data["message_kb_del"]
    file_id, media_type, format_file = message_media_type(message)

    if get_post_media_by_media_id(media_id)[0]['file_id']:
        add_post_media(
            media_id=media_id,
            message_id=str(message.message_id),
            file_id=file_id,
            media_type=media_type,
            format_file=media_type  # Формат можно также указать по необходимости
        )
    else:
        update_post_media_entry(
            media_id=media_id,
            file_id=file_id,
            media_type=media_type,
            format_file=media_type
        )

    media_group, all_message = check_media_post(media_id)

    await message.delete()
    await message.bot.delete_message(message_id=message_kb_del,
                                     chat_id=message.chat.id)
    delete_all_post_media(media_id)
    for media in all_message:
        if media.get('file_id', None):
            try:
                await message.bot.delete_message(message.chat.id, prompt_message_id)
            except:
                pass
        prompt_message_id -= 1
    delete_button_states(media_id)
    del_message_post(media_id)
    if media_group:
        sent_messages = await message.answer_media_group(media_group)
        for index, msg in enumerate(sent_messages):
            if len(media_group) > 1:
                media_id = msg.media_group_id
            else:
                media_id = msg.message_id
            chat_id = str(msg.chat.id)
            message_id = str(msg.message_id)

            # Добавляем content только для первого элемента
            content = msg.caption or msg.text or '' if index == 0 else ''
            file_id, media_type, format_file = message_media_type(msg)
            add_post_media(media_id, message_id, content, file_id, media_type, format_file, chat_id)

        add_button_states(media_id)
        add_message_post(media_id)

    await message.answer("ᅠ                               🔝                       ᅠ",
                         reply_markup=change_media_kb(media_id))
    await state.clear()  # Выходим из состояния ожидания


#  Кнопка Удалить медиа
@router.callback_query(F.data.startswith("delete_media_post:"))
async def delete_media_post(callback: types.CallbackQuery) -> None:
    media_id = callback.data.split(":")[1]
    media_group, all_message = check_media_post(media_id)
    # Создаем клавиатуру с кнопками от 1 до количества медиа
    if all_message[0]["file_id"]:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=str(i + 1),
                callback_data=f"delete_media_number:{i + 1}:{media_id}"
            )] for i in range(len(all_message))
        ])
        keyboard.inline_keyboard.extend(back_button_change_media(media_id).inline_keyboard)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    else:
        await callback.message.edit_reply_markup(reply_markup=back_button_change_media(media_id))


@router.callback_query(F.data.startswith("delete_media_number:"))
async def handle_media_delete(callback: types.CallbackQuery) -> None:
    number_media = int(callback.data.split(":")[1])
    media_id = callback.data.split(":")[-1]
    media_group, all_message = check_media_post(media_id)
    content = all_message[0]['content']
    chat_id = all_message[0]['chat_id']
    flag = all_message[0].get("flag")
    file_id = all_message[number_media - 1]['file_id']
    message_id_del = all_message[number_media - 1]['message_id']
    if len(media_group) == 1:
        delete_post_media_entry(file_id)
        await callback.bot.delete_message(chat_id=chat_id, message_id=message_id_del)
        await callback.message.delete()
        new_media_id = await callback.bot.send_message(text=content,
                                                       chat_id=chat_id)
        new_media_id = str(new_media_id.message_id)
        add_post_media(media_id=new_media_id, content=content, chat_id=chat_id, flag=flag, message_id=new_media_id)
        await callback.bot.send_message(text="ᅠ                               🔝                       ᅠ",
                                        chat_id=chat_id,
                                        reply_markup=change_media_kb(new_media_id))
    else:
        if number_media == 1:
            delete_all_post_media(media_id)
            await callback.bot.delete_message(chat_id=chat_id, message_id=message_id_del)
            update_first_media_content(media_id=media_id, content=content)
            message_id_del = int(message_id_del)
            await callback.bot.edit_message_caption(chat_id=chat_id, message_id=message_id_del, caption=content)
        else:
            delete_post_media_entry(file_id)
            await callback.bot.delete_message(chat_id=chat_id, message_id=message_id_del)
            update_first_media_content(media_id=media_id, content=content)

        await callback.message.edit_reply_markup(reply_markup=change_media_kb(media_id))


#  Кнопка изменить медиа
@router.callback_query(F.data.startswith("change_media_post:"))
async def delete_media_post(callback: types.CallbackQuery) -> None:
    media_id = callback.data.split(":")[1]
    media_group, all_message = check_media_post(media_id)
    # Создаем клавиатуру с кнопками от 1 до количества медиа
    if all_message[0]["file_id"]:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=str(i + 1),
                callback_data=f"change_media_number:{i + 1}:{media_id}"
            )] for i in range(len(all_message))
        ])
        keyboard.inline_keyboard.extend(back_button_change_media(media_id).inline_keyboard)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    else:
        await callback.message.edit_reply_markup(reply_markup=back_button_change_media(media_id))


@router.callback_query(F.data.startswith("change_media_number:"))
async def handle_media_delete(callback: types.CallbackQuery, state: FSMContext) -> None:
    number_media = int(callback.data.split(":")[1]) - 1

    media_id = callback.data.split(":")[-1]
    await callback.answer("Отправьте новое медиа")
    await state.update_data(media_id=media_id, prompt_message_id=callback.message.message_id, number_media=number_media)
    await state.set_state(MediaState.waiting_for_media_change)


@router.message(MediaState.waiting_for_media_change)
async def handle_media_input(message: types.Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    media_id = user_data["media_id"]
    number_media = user_data['number_media']
    _, all_message = check_media_post(media_id)

    old_file_id = all_message[number_media]["file_id"]
    file_id, media_type, format_file = message_media_type(message)
    new_media = create_media_list(media_type, file_id)
    update_file_id(old_file_id, file_id)

    chat_id = all_message[number_media]['chat_id']
    message_id = all_message[number_media]['message_id']
    await message.delete()
    if number_media == 0:
        await message.bot.edit_message_media(media=new_media, chat_id=chat_id, message_id=message_id)
        if caption := all_message[0]['content'] or '':
            await message.bot.edit_message_caption(caption=caption, chat_id=chat_id, message_id=message_id)

    else:
        await message.bot.edit_message_media(media=new_media, chat_id=chat_id, message_id=message_id, )

    await state.clear()  # Выходим из состояния ожидания


#  ====================================TEXT====================================================
@router.callback_query(F.data.startswith("change_text:"))
async def change_text_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    media_id = callback.data.split(":")[1]

    await callback.message.edit_text(
        text="ᅠ                               🔝                       ᅠ",
        reply_markup=change_text_kb(media_id))


@router.callback_query(F.data.startswith("change_text_post:"))
async def change_text_post_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    media_id = callback.data.split(":")[1]
    await callback.answer("Введите новый текст")
    message_del_db = await callback.message.edit_reply_markup(reply_markup=back_button_change_text(media_id))
    await state.update_data(media_id=media_id, message_del_db=message_del_db.message_id)
    await state.set_state(TextStates.waiting_for_new_text)


@router.message(TextStates.waiting_for_new_text)
async def handle_text_input(message: types.Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    media_id = user_data["media_id"]
    message_del_db = user_data["message_del_db"]
    update_first_media_content(media_id, content=message.html_text)
    update_flag_signature(media_id, flag=0)
    media_group, all_message = check_media_post(media_id)
    chat_id = all_message[0]['chat_id']
    caption = all_message[0]['content']
    message_id = all_message[0]['message_id']
    await message.delete()
    if media_group:
        await message.bot.edit_message_caption(chat_id=chat_id,
                                               message_id=message_id,
                                               caption=caption)
    else:
        await message.bot.edit_message_text(chat_id=chat_id,
                                            message_id=message_id,
                                            text=caption)
    await message.bot.edit_message_text("ᅠ                               🔝                       ᅠ",
                                        chat_id=chat_id,
                                        message_id=message_del_db,
                                        reply_markup=change_text_kb(media_id))
    await state.clear()  # Выходим из состояния ожидания


# Удаление нижней строки кода
@router.callback_query(F.data.startswith("change_text_lower_row:"))
async def change_text_lower_row_handler(callback: types.CallbackQuery) -> None:
    await callback.answer()
    media_id = callback.data.split(":")[1]
    all_message = get_post_media_by_media_id(media_id)
    new_message = all_message[0]['content'].split('\n')
    if len(new_message) > 1:
        update_first_media_content(media_id, "\n".join(new_message[:-1]))
        media_group, all_message = check_media_post(media_id)

        chat_id = all_message[0]['chat_id']
        caption = all_message[0]['content']
        message_id = all_message[0]['message_id']
        if media_group:
            await callback.bot.edit_message_caption(chat_id=chat_id,
                                                    message_id=message_id,
                                                    caption=caption)
        else:
            await callback.bot.edit_message_text(chat_id=chat_id,
                                                 message_id=message_id,
                                                 text=caption)
