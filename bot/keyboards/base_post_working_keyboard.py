from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def base_post_working_kb(media_id: str):
    base_post_working_kb_ = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отправить пост", callback_data=f"send_post:{media_id}")],
            [InlineKeyboardButton(text="Изменить", callback_data=f"change_post:{media_id}")],
            [InlineKeyboardButton(text="Удалить", callback_data="close_window")],
        ]
    )
    return base_post_working_kb_

