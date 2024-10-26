from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

base_post_working_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Отправить пост", callback_data="send_post")],
        [InlineKeyboardButton(text="Изменить", callback_data="change_post")],
        [InlineKeyboardButton(text="Удалить", callback_data="close_window")],
    ]
)
