import re

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import ADMIN
from database.db import get_users_with_rights, select_channels_publish, select_samples, select_groups_vk


def is_admin(user_id):
    admins = get_users_with_rights()
    admin_list = []
    for admin in admins:
        if admin[3]:
            admin_list.append(admin[0])
    if str(user_id) in admin_list or int(ADMIN) == int(user_id):
        return True
    else:
        return False


def start_admin_panel_kb(user_id: int):
    admin_panel_kb_ = [
        [KeyboardButton(text="📝 Новый пост")],
        [KeyboardButton(text="▶️ Очередь ВК"), KeyboardButton(text="💎 Очередь в ТГ")],
        [KeyboardButton(text="⛔ Настройка шаблонов удаления")]
    ]
    if is_admin(user_id):
        admin_panel_kb_.append([KeyboardButton(text="🅰️ Админ панель")])

    return ReplyKeyboardMarkup(keyboard=admin_panel_kb_, resize_keyboard=True)


def settings_user():
    settings_user_ = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="📝 Добавить данные", callback_data="settings_data"),
            ],
            [
                InlineKeyboardButton(text="⛔ Закрыть", callback_data="delete_settings"),
            ]
        ]
    )
    return settings_user_


def settings_parser_kb():
    settings_parser_kb_ = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="➕ Добавить", callback_data="add_source"),
                InlineKeyboardButton(text="➖ Удалить", callback_data="del_source"),
            ],
            [
                InlineKeyboardButton(text="✔️ Запустить", callback_data="start_parser"),
            ],
            [
                InlineKeyboardButton(text="❌ Остановить", callback_data="stop_parser"),
            ],
            [
                InlineKeyboardButton(text="⏪ Назад", callback_data="back_admin_panel"),
            ]
        ]
    )
    return settings_parser_kb_


def back_settings_user():
    back_settings_user_ = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="⏪ Назад", callback_data="back_settings_data"),
            ],
        ]
    )
    return back_settings_user_


def back_add_sources():
    back_add_sources_ = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="⏪ Назад", callback_data="back_add_sources"),
            ],
        ]
    )
    return back_add_sources_


def admin_panel_kb():
    admin_panel_kb_ = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="👨‍👨‍👦‍👦 Настройка пользователей", callback_data="edit_users"),
            ],
            [
                InlineKeyboardButton(text="💎 Каналы телеграм", callback_data="edit_channel"),
            ],
            [
                InlineKeyboardButton(text="🗣 Группы ВКонтакте", callback_data="groups_vkontakte"),
            ],
            [
                InlineKeyboardButton(text="📰 Источники", callback_data="source_admin")
            ],
            [
                InlineKeyboardButton(text="🕹️ Настройка чата", callback_data="edit_parser"),
            ],
            [
                InlineKeyboardButton(text="🤖 Настройки юзербота", callback_data="go_in_userbot_kb"),
            ],
            [
                InlineKeyboardButton(text="❌ Закрыть", callback_data="delete_admin_panel"),
            ]
        ]
    )
    return admin_panel_kb_


def admin_panel_edit_users_kb():
    admin_panel_edit_users_kb_ = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="➕ Добавить", callback_data="edit_users_add"),
                InlineKeyboardButton(text="➖ Удалить", callback_data="edit_users_del"),
            ],
            [
                InlineKeyboardButton(text="⬆️ Повысить", callback_data="add_all_rights"),
                InlineKeyboardButton(text="⬇️ Понизить", callback_data="del_all_rights"),
            ],
            [
                InlineKeyboardButton(text="⏪ Назад", callback_data="back_admin_panel"),
            ],
        ]
    )
    return admin_panel_edit_users_kb_


def back_edit_users_kb():
    back_edit_users_kb_ = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="⏪ Назад", callback_data="back_edit_users"),
            ],
        ]
    )
    return back_edit_users_kb_


def back_edit_channel_kb():
    back_edit_channel_kb_ = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="⏪ Назад", callback_data="back_edit_channel"),
            ],
        ]
    )
    return back_edit_channel_kb_


def admin_panel_edit_channel_kb():
    admin_panel_edit_channel_kb_ = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="➕ Добавить", callback_data="edit_channel_add"),
                InlineKeyboardButton(text="➖ Удалить", callback_data="edit_channel_del"),
            ],
            [
                InlineKeyboardButton(text="⏪ Назад", callback_data="back_admin_panel"),
            ],
        ]
    )
    return admin_panel_edit_channel_kb_


def admin_panel_edit_parser_kb():
    admin_panel_edit_parser_kb_ = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="📑 Изменить", callback_data="edit_edit_parser"),
            ],
            [
                InlineKeyboardButton(text="⏪ Назад", callback_data="back_admin_panel"),
            ],
        ]
    )
    return admin_panel_edit_parser_kb_


def back_edit_parser():
    back_edit_parser_ = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="⏪ Назад", callback_data="back_edit_parser"),
            ],
        ]
    )
    return back_edit_parser_


def back_change_signature_kb():
    back_admin_panel_kb_ = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="⏪ Назад", callback_data="back_change_signature"),
            ],
        ]
    )
    return back_admin_panel_kb_


def delete_users_with_rights():
    builder = InlineKeyboardBuilder()
    users = get_users_with_rights()
    for user_id, username, rights_post, rights_all in users:
        if rights_post and not rights_all:
            builder.row(InlineKeyboardButton(text=f"✏️ {username} {user_id}", callback_data=f"rights_delete_{user_id}"))
        else:
            builder.row(InlineKeyboardButton(text=f"🔓 {username} {user_id}", callback_data=f"rights_delete_{user_id}"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data="back_edit_users"))
    return builder.as_markup()


def add_all_rights_kb():
    builder = InlineKeyboardBuilder()
    users = get_users_with_rights()
    for user_id, username, rights_post, rights_all in users:
        if rights_post and not rights_all:
            builder.row(
                InlineKeyboardButton(text=f"✏️ {username} {user_id}", callback_data=f"rights_add_all_{user_id}"))
        else:
            builder.row(InlineKeyboardButton(text=f"🔓 {username} {user_id}", callback_data=f"rights_add_all_{user_id}"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data="back_edit_users"))
    return builder.as_markup()


def del_all_rights_kb():
    builder = InlineKeyboardBuilder()
    users = get_users_with_rights()
    for user_id, username, rights_post, rights_all in users:
        if rights_post and not rights_all:
            builder.row(
                InlineKeyboardButton(text=f"✏️ {username} {user_id}", callback_data=f"rights_del_all_{user_id}"))
        else:
            builder.row(InlineKeyboardButton(text=f"🔓 {username} {user_id}", callback_data=f"rights_del_all_{user_id}"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data="back_edit_users"))
    return builder.as_markup()


def delete_channels_kb():
    builder = InlineKeyboardBuilder()
    channels = select_channels_publish()
    for channel_username, channel_id in channels:
        builder.row(InlineKeyboardButton(text=f"{channel_username}", callback_data=f"channel_del_{channel_id}"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data="back_edit_channel"))
    return builder.as_markup()


def get_samples_kb():
    builder = InlineKeyboardBuilder()
    samples = select_samples()
    for _id, text in samples:
        text = re.sub('<.*?>', '', text)
        builder.row(InlineKeyboardButton(text=f"{text}", callback_data=f"get_sample_{_id}"))
    builder.row(InlineKeyboardButton(text="➕ Добавить", callback_data=f"add_sample"),
                InlineKeyboardButton(text="➖ Удалить", callback_data=f"delete_sample"))
    builder.row(InlineKeyboardButton(text="❌ Закрыть", callback_data="delete_admin_panel"))
    return builder.as_markup()


def delete_samples():
    builder = InlineKeyboardBuilder()
    samples = select_samples()
    for _id, text in samples:
        builder.row(InlineKeyboardButton(text=f"🚫 {text}", callback_data=f"samp_delete_{_id}"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data="back_change_signature"))
    return builder.as_markup()


def settings_user_already():
    settings_user_already_ = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="📝 Изменить данные", callback_data="settings_data"),
            ],
            [
                InlineKeyboardButton(text="🔁 Перезапустить клиент", callback_data="restart_client"),
            ],
            [
                InlineKeyboardButton(text="Мягкая остановка", callback_data="soft_stop"),
            ],
            [
                InlineKeyboardButton(text="Мягкий старт", callback_data="soft_start"),
            ],
            [
                InlineKeyboardButton(text="⏪ Назад", callback_data="back_admin_panel"),
            ]
        ]
    )
    return settings_user_already_


def back_to_userbot_kb():
    back_to_userbot_kb_ = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="⏪ Назад", callback_data="go_in_userbot_kb"),
            ],
        ]
    )
    return back_to_userbot_kb_


def group_vkontakte():
    builder = InlineKeyboardBuilder()
    groups = select_groups_vk()
    for group in groups:
        if group[2]:
            builder.row(InlineKeyboardButton(text=f"✔️ {group[0]}", callback_data=f"off_on_group_vk:{group[1]}"))
        else:
            builder.row(InlineKeyboardButton(text=f"❌ {group[0]}", callback_data=f"off_on_group_vk:{group[1]}"))
    builder.row(InlineKeyboardButton(text="➕ Добавить", callback_data="add_group_vkontakte"),
                InlineKeyboardButton(text="➖ Удалить", callback_data="delete_group_vkontakte"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data="back_admin_panel"))

    return builder.as_markup()


def edit_groups_vkontakte_kb():
    edit_groups_vkontakte_kb_ = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="⏪ Назад", callback_data="groups_vkontakte"),
            ],
        ]
    )
    return edit_groups_vkontakte_kb_
