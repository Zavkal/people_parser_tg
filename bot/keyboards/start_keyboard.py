from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def start_kb(media_id: str):
    start_kb_ = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Начать", callback_data=f"start_working:{media_id}")],
            [InlineKeyboardButton(text="❌ Удалить", callback_data=f"close_window:{media_id}")],
        ]
    )
    return start_kb_


def start_kb_middleware(media_id: str):
    start_kb_middleware_ = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Начать", callback_data=f"start_working:{media_id}")],
            [InlineKeyboardButton(text="❌ Удалить", callback_data=f"close_window:{media_id}")],
        ]
    )
    return start_kb_middleware_

