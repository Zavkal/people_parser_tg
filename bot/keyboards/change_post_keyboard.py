from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

change_post_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Изменить описание", callback_data="change_description")],
        [InlineKeyboardButton(text="Изменить медиа", callback_data="change_media")],
        [InlineKeyboardButton(text="Изменить текст", callback_data="change_text")],
        [InlineKeyboardButton(text="⏪ Назад", callback_data="start_working")],
    ]
)

change_description_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить", callback_data="add_description"),
            InlineKeyboardButton(text="➖ Удалить", callback_data="remove_description")],
        [InlineKeyboardButton(text="⏪ Назад", callback_data="change_post")],
    ]
)

back_to_change_description_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⏪ Назад", callback_data="change_description")],
    ]
)

change_media_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⏪ Назад", callback_data="change_post")],
    ]
)

change_text_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⏪ Назад", callback_data="change_post")],
    ]
)
