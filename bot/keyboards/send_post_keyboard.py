from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

send_post_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Отправить сейчас", callback_data="send_post_now")],
        [InlineKeyboardButton(text="Отправить завтра", callback_data="send_post_tomorrow")],
        [InlineKeyboardButton(text="Отправить по времени", callback_data="send_post_by_time")],
        [InlineKeyboardButton(text="Назад", callback_data="start_working")],
    ]
)

send_post_base_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Отправить в ТГ", callback_data="send_to_tg")],
        [InlineKeyboardButton(text="Отправить в ВК", callback_data="send_to_vk")],
        [InlineKeyboardButton(text="Назад", callback_data="send_post")],
    ]
)


send_post_tomorrow_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Указать время", callback_data="choose_time")],
        [InlineKeyboardButton(text="Назад", callback_data="send_post")],
    ]
)


send_post_by_time_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Указать дату и время", callback_data="choose_date_and_time")],
        [InlineKeyboardButton(text="Назад", callback_data="send_post")],
    ]
)
