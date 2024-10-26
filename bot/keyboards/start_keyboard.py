from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Начать", callback_data="start_working")],
        [InlineKeyboardButton(text="Удалить", callback_data="close_window")],
    ]
)
