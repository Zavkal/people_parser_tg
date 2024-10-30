from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def change_post_kb(media_id):
    change_post_kb_ = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Изменить описание", callback_data=f"change_description:{media_id}")],
            [InlineKeyboardButton(text="Изменить медиа", callback_data=f"change_media:{media_id}")],
            [InlineKeyboardButton(text="Изменить текст", callback_data=f"change_text:{media_id}")],
            [InlineKeyboardButton(text="⏪ Назад", callback_data=f"start_working:{media_id}")],
        ]
    )
    return change_post_kb_


def change_description_kb(media_id: str):
    change_description_kb_ = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить", callback_data=f"add_description:{media_id}"),
             InlineKeyboardButton(text="➖ Удалить", callback_data=f"remove_description:{media_id}")],
            [InlineKeyboardButton(text="⏪ Назад", callback_data=f"change_post:{media_id}")],
        ]
    )
    return change_description_kb_


def back_to_change_description_kb(media_id: str):
    back_to_change_description_kb_ = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⏪ Назад", callback_data=f"change_description:{media_id}")],
        ]
    )
    return back_to_change_description_kb_


def change_media_kb(media_id: str):
    change_media_kb_ = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Изменить", callback_data=f"change_media_post:{media_id}")],
            [InlineKeyboardButton(text="Удалить", callback_data=f"delete_media_post:{media_id}"),
             InlineKeyboardButton(text="Добавить", callback_data=f"add_media_post:{media_id}")],
            [InlineKeyboardButton(text="Назад", callback_data=f"change_post:{media_id}")],
        ]
    )
    return change_media_kb_


def change_text_kb(media_id: str):
    change_text_kb_ = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Изменить текст.", callback_data=f"change_text_post:{media_id}"),
             InlineKeyboardButton(text="Удалить нижнюю строку.", callback_data=f":{media_id}")],
            [InlineKeyboardButton(text="⏪ Назад", callback_data=f"change_post:{media_id}")]
        ]
    )

    return change_text_kb_


def back_button_change_text(media_id: str):
    change_text_kb_ = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⏪ Назад", callback_data=f"change_text:{media_id}")]
        ]
    )

    return change_text_kb_


def back_button_change_post(media_id: str):
    back_button_change_post_ = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data=f"change_post:{media_id}")]
    ])
    return back_button_change_post_


def back_button_change_media(media_id: str):
    back_button_change_post_ = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data=f"change_media:{media_id}")]
    ])
    return back_button_change_post_
