from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import get_sources, get_parser_info


def get_sources_for_del():
    builder = InlineKeyboardBuilder()
    sources = get_sources()
    for _id, title in sources:
        builder.row(InlineKeyboardButton(text=f"🚫 {title}", callback_data=f"source_del_{_id}"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data=f"back_add_sources"))
    return builder.as_markup()


def get_started_kb(_type):
    builder = InlineKeyboardBuilder()
    parsers = get_sources()
    for _id, title in parsers:
        if get_parser_info(title):
            builder.row(InlineKeyboardButton(text=f"✅ {title}", callback_data=f"{_type}_source_{title}"))
        else:
            builder.row(InlineKeyboardButton(text=f"❌ {title}", callback_data=f"{_type}_source_{title}"))
    if _type == "start":
        builder.row(InlineKeyboardButton(text="✅ Запустить все ✅", callback_data=f"start_all_parser"))
    else:
        builder.row(InlineKeyboardButton(text="❌ Остановить все ❌", callback_data=f"stop_all_parser"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data=f"back_add_sources"))
    return builder.as_markup()