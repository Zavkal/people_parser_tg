from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import get_button_states, get_one_post_message


def send_post_kb(media_id: str):
    send_post_kb_ = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="☑️ Сейчас", callback_data=f"send_post_now:{media_id}")],
            [InlineKeyboardButton(text="⏱️ Сегодня", callback_data=f"send_post_today:{media_id}"),
             InlineKeyboardButton(text="🧭 Завтра", callback_data=f"send_post_tomorrow:{media_id}")],
            [InlineKeyboardButton(text="📅 По дате", callback_data=f"send_post_by_time:{media_id}"),
             InlineKeyboardButton(text="⏪ Назад", callback_data=f"start_working:{media_id}")],
        ]
    )
    return send_post_kb_


def send_post_base_kb(media_id: str):
    builder = InlineKeyboardBuilder()
    button_states = get_button_states(media_id)
    post_time = get_one_post_message(media_id)
    if button_states:
        button_tg_state, button_vk_state = button_states

        # Если кнопка для Telegram отправлена (on), показываем кнопку с "✅"
        if button_tg_state == "on":
            builder.row(InlineKeyboardButton(text=f"✅ {post_time[1][:-3] if post_time[1] else 'Отправлен в'} 💎 ТГ", callback_data="error"))
        else:
            builder.row(InlineKeyboardButton(text="☑️ Отправить в 💎 ТГ", callback_data=f"send_to_tg:{media_id}"))

        # Если кнопка для ВК отправлена (on), показываем кнопку с "✅"
        if button_vk_state == "on":
            builder.row(InlineKeyboardButton(text=f"✅ {post_time[2][:-3] if post_time[2] else 'Отправлен в'} ➡️ ВК", callback_data="error"))
        else:
            builder.row(InlineKeyboardButton(text="☑️ Отправить в ➡️ ВК", callback_data=f"send_to_vk:{media_id}"))

    else:
        builder.row(InlineKeyboardButton(text="☑️ Отправить в 💎 ТГ", callback_data=f"send_to_tg:{media_id}"))
        builder.row(InlineKeyboardButton(text="☑️ Отправить в ➡️ ВК", callback_data=f"send_to_vk:{media_id}"))

    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data=f"send_post:{media_id}"))
    return builder.as_markup()


def kb_back_send_post(media_id: str):
    kb_back_send_post_ = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⏪ Назад", callback_data=f"send_post:{media_id}")],
        ]
    )
    return kb_back_send_post_
