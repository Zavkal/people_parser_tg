import re

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.keyboards.change_post_keyboard import (
    back_to_change_description_kb, change_description_kb,
    change_media_kb,
    change_post_kb, change_text_kb
)
from database.db import get_all_signatures, add_signature, delete_signature

router = Router(name="Изменение поста")


@router.callback_query(F.data == "change_post")
async def change_post_handler(
    callback: types.CallbackQuery,
) -> None:
    await callback.message.edit_reply_markup(
        reply_markup=change_post_kb
    )


# ====================================DESCRIPTION====================================================
@router.callback_query(F.data == "change_description")
async def change_description_handler(callback: types.CallbackQuery) -> None:
    signatures = get_all_signatures()

    if signatures:
        inline_keyboard = []

        for signature in signatures:
            button = InlineKeyboardButton(
                text=signature['title'],
                callback_data=f"signature_{signature['id']}"
            )
            inline_keyboard.append([button])  # Каждый элемент - это список кнопок (для одной кнопки)

        for row in change_description_kb.inline_keyboard:
            inline_keyboard.append(row)

            # Создаем InlineKeyboardMarkup с указанием inline_keyboard
        keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    await callback.message.edit_reply_markup(reply_markup=keyboard)



class DescriptionStates(StatesGroup):
    waiting_for_description = State()
    waiting_for_new_signature = State()


@router.callback_query(F.data == "add_description")
async def add_description_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.answer(
        text="Введите новое описание:",
        reply_markup=back_to_change_description_kb
    )
    # Устанавливаем состояние для ожидания ввода текста
    await state.set_state(DescriptionStates.waiting_for_description)


@router.callback_query(DescriptionStates.waiting_for_description)
async def save_description_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    # Скрываем все кнопки и показываем только кнопку "Назад"
    back_button_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
    ])

    # Отправляем сообщение о необходимости ввести новую подпись
    await callback.message.edit_text("Введите новую подпись:", reply_markup=back_button_kb)

    # Сохраняем состояние для ожидания текста
    await state.set_state(DescriptionStates.waiting_for_new_signature)


@router.message(DescriptionStates.waiting_for_new_signature)
async def handle_new_signature(message: types.Message, state: FSMContext) -> None:
    new_description = message.text  # Получаем текст от пользователя

    # Сохранение в БД
    add_signature(new_description)  # Функция для добавления описания в БД

    # Подтверждаем добавление и возвращаемся к клавиатуре с подписями
    signatures = get_all_signatures()  # Получаем все подписи для обновления клавиатуры

    # Создаем клавиатуру с оставшимися подписями, включая новую
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"Удалить: {signature['title']} (ID: {signature['id']})",
            callback_data=f"remove_signature_{signature['id']}"
        )] for signature in signatures
    ])

    # Добавляем кнопку "Назад"
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="Вернуться назад", callback_data="back_to_menu")
    ])

    # Обновляем сообщение с новой клавиатурой
    await message.answer("Подпись добавлена. Выберите действие:", reply_markup=keyboard)

    # Сбрасываем состояние
    await state.clear()


@router.callback_query(F.data == "remove_description")
async def remove_signature_handler(callback: types.CallbackQuery) -> None:
    signatures = get_all_signatures()  # Функция для получения всех подписей после удаления

    if signatures:
        # Создаем клавиатуру с оставшимися подписями
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=f"Удалить: {signature['title']} (ID: {signature['id']})",
                callback_data=f"remove_signature_{signature['id']}"
            )] for signature in signatures
        ])

        # Добавляем кнопку "Назад"
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="⏪ Назад", callback_data="change_post")
        ])

        # Обновляем сообщение с новой клавиатурой
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    else:
        # Если нет оставшихся подписей, оставляем только кнопку "Назад"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏪ Назад", callback_data="change_post")]
        ])
        await callback.message.edit_reply_markup(reply_markup=keyboard)

    await callback.answer()  # Завершаем обработку колбека@router.callback_query(F.data == "remove_description")


async def show_signatures_handler(callback: types.CallbackQuery) -> None:
    signatures = get_all_signatures()  # Функция для получения всех подписей после удаления

    if signatures:
        # Создаем клавиатуру с оставшимися подписями
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=f"Удалить: {signature['title']} (ID: {signature['id']})",
                callback_data=f"remove_signature_{signature['id']}"
            )] for signature in signatures
        ])

        # Добавляем кнопку "Назад"
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="⏪ Назад", callback_data="change_post")
        ])

        # Обновляем сообщение с новой клавиатурой
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    else:
        # Если нет оставшихся подписей, оставляем только кнопку "Назад"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏪ Назад", callback_data="change_post")]
        ])
        await callback.message.edit_reply_markup(reply_markup=keyboard)

    await callback.answer()  # Завершаем обработку колбека


@router.callback_query(F.data.startswith("remove_signature_"))
async def remove_signature_handler(callback: types.CallbackQuery) -> None:
    # Извлекаем ID подписи из callback_data
    signature_id = callback.data.split("_")[-1]

    # Удаляем подпись из базы данных
    delete_signature(int(signature_id))  # Вызов функции удаления

    # Получаем обновленный список подписей
    signatures = get_all_signatures()

    if signatures:
        # Создаем клавиатуру с оставшимися подписями
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=f"Удалить: {signature['title']} (ID: {signature['id']})",
                callback_data=f"remove_signature_{signature['id']}"
            )] for signature in signatures
        ])

        await callback.message.edit_reply_markup(reply_markup=keyboard)
    else:
        # Если нет оставшихся подписей, оставляем только кнопку "Назад"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏪ Назад", callback_data="change_post")]
        ])
        await callback.message.edit_reply_markup(reply_markup=keyboard)

    await callback.answer("Подпись удалена.")  # Подтверждаем удаление



# ====================================MEDIA====================================================
@router.callback_query(F.data == "change_media")
async def change_media_handler(
    callback: types.CallbackQuery,
) -> None:
    await callback.message.edit_text(
        text="Отправьте новое медиа",
        reply_markup=change_media_kb
    )


# ====================================TEXT====================================================
@router.callback_query(F.data == "change_text")
async def change_text_handler(
    callback: types.CallbackQuery,
) -> None:
    await callback.message.edit_text(
        text="Отправьте новый текст",
        reply_markup=change_text_kb
    )
