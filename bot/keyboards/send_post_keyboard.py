from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import get_all_publ_time, get_button_states


def send_post_kb(media_id: str):
    send_post_kb_ = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отправить сейчас", callback_data=f"send_post_now:{media_id}")],
            [InlineKeyboardButton(text="Отправить сегодня", callback_data=f"send_post_today:{media_id}")],
            [InlineKeyboardButton(text="Отправить завтра", callback_data=f"send_post_tomorrow:{media_id}")],
            [InlineKeyboardButton(text="Отправить по времени", callback_data=f"send_post_by_time:{media_id}")],
            [InlineKeyboardButton(text="Назад", callback_data="start_working")],
        ]
    )
    return send_post_kb_


def send_post_base_kb(media_id: str):
    builder = InlineKeyboardBuilder()
    button_states = get_button_states(media_id)
    if button_states:
        button_tg_state, button_vk_state = button_states

        # Если кнопка для Telegram отправлена (on), показываем кнопку с "✅"
        if button_tg_state == "on":
            builder.row(InlineKeyboardButton(text="✅ Отправлен в 💎 ТГ", callback_data="tg_state"))
        else:
            builder.row(InlineKeyboardButton(text="☑️ Отправить в 💎 ТГ", callback_data=f"send_to_tg:{media_id}"))

        # Если кнопка для ВК отправлена (on), показываем кнопку с "✅"
        if button_vk_state == "on":
            builder.row(InlineKeyboardButton(text="✅ Отправлен в ➡️ ВК", callback_data="vk_state"))
        else:
            builder.row(InlineKeyboardButton(text="☑️ Отправить в ➡️ ВК", callback_data=f"send_to_vk:{media_id}"))

    else:
        builder.row(InlineKeyboardButton(text="☑️ Отправить в 💎 ТГ", callback_data=f"send_to_tg:{media_id}"))
        builder.row(InlineKeyboardButton(text="☑️ Отправить в ➡️ ВК", callback_data=f"send_to_vk:{media_id}"))

    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data=f"send_post:{media_id}"))
    return builder.as_markup()


def send_post_tomorrow_kb(media_id: str):
    send_post_tomorrow_kb_ = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Указать время", callback_data=f"choose_time:{media_id}")],
            [InlineKeyboardButton(text="Назад", callback_data=f"send_post:{media_id}")],
        ]
    )
    return send_post_tomorrow_kb_


def send_post_today_kb(media_id: str):
    send_post_today_kb_ = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Указать время", callback_data=f"choose_time:{media_id}")],
            [InlineKeyboardButton(text="Назад", callback_data=f"send_post:{media_id}")],
        ]
    )
    return send_post_today_kb_


def send_post_by_time_kb(media_id: str):
    send_post_by_time_kb_ = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Указать дату и время", callback_data=f"choose_date_and_time:{media_id}")],
            [InlineKeyboardButton(text="Назад", callback_data=f"send_post:{media_id}")],
        ]
    )
    return send_post_by_time_kb_


def kb_back_send_post(media_id: str):
    kb_back_send_post_ = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data=f"send_post:{media_id}")],
        ]
    )
    return kb_back_send_post_

