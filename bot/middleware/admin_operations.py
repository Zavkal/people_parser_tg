from database.db import get_users_with_rights, get_user_with_rights, delete_user_with_rights, select_chat, \
    select_channels_publish


def _get_users_with_rights():
    users = get_users_with_rights()
    text_list = []
    for user_id, username, rights_post, rights_all in users:
        if rights_post and not rights_all:
            text = f"✏️ {username} {user_id}"
        else:
            text = f"🔓 {username} {user_id}"

        text_list.append(text)
    return "\n".join(text_list)


def delete_user(user_id: str):
    if get_user_with_rights(user_id):
        delete_user_with_rights(user_id)
        return True
    else:
        return False


def get_chat():
    if select_chat():
        chat_id, username = select_chat()
        return f"@{username}"
    else:
        return ""


def get_channels():
    channels = [f"@{info[0]}" for info in select_channels_publish()]
    return "\n".join(channels)


def get_channels_ids():
    ids = [data[1] for data in select_channels_publish()]
    return ids


def get_users_id_with_rights():
    ids = [data[0] for data in get_users_with_rights()]
    return ids


def get_users_id_with_all_rights():
    ids = [data[0] for data in get_users_with_rights() if data[3]]
    return ids


def get_id_for_mg(mess_id: str, user_id: str):
    return f"{mess_id}_{user_id}"

