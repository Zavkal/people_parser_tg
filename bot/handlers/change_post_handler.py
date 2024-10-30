import asyncio
import re
import time

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.handlers.pars_message_chat import message_media_type
from bot.keyboards.change_post_keyboard import (
    change_description_kb,
    change_media_kb,
    change_post_kb, change_text_kb, back_button_change_post, back_to_change_description_kb, back_button_change_media,
    back_button_change_text
)
from bot.middleware.autodel_create_message import autodel_create_mg, autodel_create_mg_
from bot.middleware.check_media import check_media_post
from bot.middleware.create_media_list import create_media_list
from database.db import get_all_signatures, add_signature, delete_signature, get_signature_by_id, \
    get_post_media_by_media_id, update_post_content, add_post_media, update_post_media_entry, \
    delete_post_media_entry, update_file_id, update_first_media_content

router = Router(name="Изменение поста")


class TextStates(StatesGroup):
    waiting_for_new_signature = State()
    waiting_for_new_text = State()

class MediaState(StatesGroup):
    waiting_for_media = State()
    waiting_for_media_number = State()
    waiting_for_media_change = State()


@router.callback_query(F.data.startswith("change_post:"))
async def change_post_handler(
        callback: types.CallbackQuery
) -> None:
    media_id = callback.data.split(":")[1]
    media_group, all_message = check_media_post(media_id)

    await autodel_create_mg(callback, all_message, media_group)

    await callback.message.answer(text="Изменить пост", reply_markup=change_post_kb(media_id=media_id))


# ====================================DESCRIPTION====================================================
@router.callback_query(F.data.startswith("change_description:"))
async def change_description_handler(callback: types.CallbackQuery) -> None:
    media_id = callback.data.split(":")[1]
    media_group, all_message = check_media_post(media_id)
    signatures = get_all_signatures()  # Получаем все подписи
    inline_keyboard = []  # Создаем список для кнопок

    await autodel_create_mg(callback, all_message, media_group)
    if signatures:
        for signature in signatures:
            title = signature.get('title', None)
            if title:
                button = InlineKeyboardButton(
                    text=title,
                    callback_data=f"signature:{signature['id']}:{media_id}"
                    # Уникальный callback_data для каждой кнопки
                )
                inline_keyboard.append([button])  # Каждая кнопка в отдельной строке

    # Создаем InlineKeyboardMarkup с указанием inline_keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    # Объединяем обе клавиатуры
    keyboard.inline_keyboard.extend(change_description_kb(media_id).inline_keyboard)

    # Редактируем сообщение с новой клавиатурой
    await callback.message.answer("Выберите подпись", reply_markup=keyboard)


@router.callback_query(F.data.startswith("signature:"))
async def handle_signature_selection(callback: types.CallbackQuery) -> None:
    signature_id = callback.data.split(":")[1]  # Получаем ID подписи
    media_id = callback.data.split(":")[-1]
    signature = get_signature_by_id(signature_id)  # Получаем подпись по ID из БД
    if signature:
        new_signature_text = f"\n\n{signature['title']}"  # Подготавливаем новый текст
        if get_post_media_by_media_id(media_id=media_id)[0]['content']:
            new_content = get_post_media_by_media_id(media_id=media_id)[0]['content'] + new_signature_text
            update_post_content(media_id, new_content)
        else:
            update_post_content(media_id, new_signature_text)
        media_group, all_message = check_media_post(media_id)
        await autodel_create_mg(callback, all_message, media_group)
        await callback.message.answer("Выберите действие", reply_markup=change_post_kb(media_id))


@router.callback_query(F.data.startswith("add_description:"))
async def add_description_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    # Показываем только кнопку "Назад"
    media_id = callback.data.split(":")[1]
    await state.update_data(media_id=media_id)
    back_button_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data=f"change_description:{media_id}")]
    ])

    # Подтверждаем нажатие кнопки и отправляем клавиатуру
    await callback.answer("Введите подпись")
    await callback.message.edit_reply_markup(reply_markup=back_button_kb)

    # Сохраняем состояние для ожидания текста
    await state.set_state(TextStates.waiting_for_new_signature)


@router.message(TextStates.waiting_for_new_signature)
async def handle_new_signature(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    media_id = data.get('media_id')
    new_description = message.text

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
                button = InlineKeyboardButton(
                    text=title,
                    callback_data=f"signature_{signature['id']}"  # Уникальный callback_data для каждой кнопки
                )
                inline_keyboard.append([button])  # Каждая кнопка в отдельной строке

    # Создаем InlineKeyboardMarkup с кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    keyboard.inline_keyboard.extend(change_description_kb(media_id).inline_keyboard)  # Объединяем клавиатуры

    # Отправляем клавиатуру без изменения текста сообщения
    await message.answer(text="Выберите действие (После добавления подписи)", reply_markup=keyboard)

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
    # Извлекаем ID подписи из callback_data
    signature_id = callback.data.split(":")[1]
    media_id = callback.data.split(":")[-1]

    # Удаляем подпись из базы данных
    delete_signature(int(signature_id))  # Вызов функции удаления

    # Получаем обновленный список подписей
    signatures = get_all_signatures()

    if signatures:
        # Создаем клавиатуру с оставшимися подписями
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=f"Удалить: {signature['title']} (ID: {signature['id']})",
                callback_data=f"remove_signature:{signature['id']}:{media_id}"
            )] for signature in signatures
        ])

        # Добавляем кнопку "Назад"
        keyboard.inline_keyboard.append(back_to_change_description_kb(media_id))

        # Обновляем сообщение с новой клавиатурой
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    else:
        await callback.message.edit_reply_markup(reply_markup=back_to_change_description_kb(media_id))

    await callback.answer("Подпись удалена.")  # Подтверждаем удаление


# ====================================MEDIA====================================================
@router.callback_query(F.data.startswith("change_media:"))
async def change_media_handler(
        callback: types.CallbackQuery,
) -> None:
    media_id = callback.data.split(":")[1]
    media_group, all_message = check_media_post(media_id)

    await autodel_create_mg(callback, all_message, media_group)

    # Отправляем текстовое сообщение, если контент существует

    await callback.message.answer(
        text="Выберите действие.",
        reply_markup=change_media_kb(media_id))


#  Кнопка Добавить медиа
@router.callback_query(F.data.startswith("add_media_post:"))
async def add_media_post(callback: types.CallbackQuery, state: FSMContext) -> None:
    media_id = callback.data.split(":")[1]
    await callback.answer("Отправьте медиа для добавления.")
    await callback.message.edit_reply_markup(reply_markup=back_button_change_media(media_id))
    await state.update_data(media_id=media_id, prompt_message_id=callback.message.message_id)
    await state.set_state(MediaState.waiting_for_media)


@router.message(MediaState.waiting_for_media)
async def handle_media_input(message: types.Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    media_id = user_data["media_id"]
    # Получаем id сообщения из состояния для удаления.
    prompt_message_id = user_data["prompt_message_id"]
    await message.bot.delete_message(chat_id=message.chat.id, message_id=prompt_message_id)
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

    await autodel_create_mg_(message, all_message, media_group, prompt_message_id)
    # Очищаем состояние и возвращаем клавиатуру
    await message.answer('Выберите действие', reply_markup=change_media_kb(media_id))
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
    user_id = all_message[0]['user_id']
    file_id = all_message[number_media-1]['file_id']
    if number_media == 1:
        await autodel_create_mg(callback, all_message, media_group)
        delete_post_media_entry(file_id)
        if get_post_media_by_media_id(media_id):
            update_post_content(
                media_id=media_id,
                content=content
            )
        else:
            add_post_media(
                media_id=media_id,
                message_id=media_id,
                content=content,
                user_id=user_id
            )
    else:
        counter = callback.message.message_id
        for media in all_message:
            counter -= 1
            if media.get('file_id', None):
                try:
                    await callback.bot.delete_message(int(all_message[0]['user_id']), counter)
                except:
                    pass
        delete_post_media_entry(file_id)

    media_group, all_message = check_media_post(media_id)
    if media_group:
        await callback.message.answer_media_group(media_group)
    else:
        try:
            await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id - 1)
        except:
            pass
        await callback.message.answer(all_message[0]['content'])
    await callback.message.answer('Выберите действие', reply_markup=change_media_kb(media_id))


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
    await callback.message.edit_reply_markup(reply_markup=change_media_kb(media_id))
    await state.update_data(media_id=media_id, prompt_message_id=callback.message.message_id, number_media=number_media)
    await state.set_state(MediaState.waiting_for_media_change)


@router.message(MediaState.waiting_for_media_change)
async def handle_media_input(message: types.Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    media_id = user_data["media_id"]
    number_media = user_data['number_media']
    prompt_message_id = user_data["prompt_message_id"]
    await message.bot.delete_message(chat_id=message.chat.id, message_id=prompt_message_id)

    _, all_message = check_media_post(media_id)
    old_file_id = all_message[number_media]["file_id"]
    file_id, media_type, format_file = message_media_type(message)
    update_file_id(old_file_id, file_id)
    media_group, all_message = check_media_post(media_id)
    await autodel_create_mg_(message, all_message, media_group, prompt_message_id)
    await message.answer('Выберите действие', reply_markup=back_button_change_media(media_id))
    await state.clear()  # Выходим из состояния ожидания


#  ====================================TEXT====================================================
@router.callback_query(F.data.startswith("change_text:"))
async def change_text_handler(callback: types.CallbackQuery) -> None:
    media_id = callback.data.split(":")[1]
    media_group, all_message = check_media_post(media_id)

    await autodel_create_mg(callback, all_message, media_group)

    # Отправляем текстовое сообщение, если контент существует

    await callback.message.answer(
        text="Выберите действие.",
        reply_markup=change_text_kb(media_id))


@router.callback_query(F.data.startswith("change_text_post:"))
async def change_text_handler(callback: types.CallbackQuery, state: FSMContext) -> None:

    media_id = callback.data.split(":")[1]
    await state.update_data(media_id=media_id, prompt_message_id=callback.message.message_id)
    await callback.answer("Введите новый текст")
    await callback.message.edit_reply_markup(reply_markup=back_button_change_text(media_id))
    await state.set_state(TextStates.waiting_for_new_text)


@router.message(TextStates.waiting_for_new_text)
async def handle_text_input(message: types.Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    media_id = user_data["media_id"]
    prompt_message_id = user_data["prompt_message_id"]
    await message.bot.delete_message(chat_id=message.chat.id, message_id=prompt_message_id - 1)

    update_first_media_content(media_id, content=message.text)
    media_group, all_message = check_media_post(media_id)
    await autodel_create_mg_(message, all_message, media_group, prompt_message_id)
    await message.answer('Выберите действие', reply_markup=change_text_kb(media_id))
    await state.clear()  # Выходим из состояния ожидания


# Удаление нижней строки кода
@router.callback_query(F.data.startswith("change_text_post:"))
async def change_text_handler(callback: types.CallbackQuery, state: FSMContext) -> None:

    media_id = callback.data.split(":")[1]
    await state.update_data(media_id=media_id, prompt_message_id=callback.message.message_id)
    await callback.answer("Введите новый текст")
    await callback.message.edit_reply_markup(reply_markup=back_button_change_text(media_id))


