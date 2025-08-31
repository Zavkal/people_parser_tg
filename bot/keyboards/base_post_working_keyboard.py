from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def base_post_working_kb(media_id: str):
    base_post_working_kb_ = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="☑️ Отправить пост", callback_data=f"send_post:{media_id}")
            ],
            [
                InlineKeyboardButton(text="📃 Подпись", callback_data=f"change_description:{media_id}")
            ],
            [
                InlineKeyboardButton(text="✍️ Изменить", callback_data=f"change_post:{media_id}"),
             InlineKeyboardButton(text="⏪ Назад", callback_data=f"start_kb_middleware:{media_id}")
            ],
        ]
    )
    return base_post_working_kb_
