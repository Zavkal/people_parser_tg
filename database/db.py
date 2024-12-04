import os
import sqlite3 as sq
from datetime import datetime, timedelta

base_dir = os.path.dirname(os.path.abspath(__file__))

relative_path = "db_bot.db"

db_path = os.path.join(base_dir, relative_path)

db = sq.connect(db_path)
cur = db.cursor()


async def start_db():
    cur.execute("CREATE TABLE IF NOT EXISTS who_worked("
                "user_id TEXT,"
                "caption TEXT,"
                "mess_id TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS sources("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "title TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS signatures("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "title TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS chat("
                "chat_username TEXT,"
                "chat_id TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS channel_publish("
                "channel_username TEXT,"
                "channel_id TEXT)")

    # Добавил отдельную БД для хранения сообщения и времени
    cur.execute("CREATE TABLE IF NOT EXISTS post_message("
                "media_id TEXT,"
                "publ_time_tg TEXT,"
                "publ_time_vk,"
                "del_time TEXT)")

    # Добавил бд с путями до файлов с привязкой по post_id
    cur.execute("CREATE TABLE IF NOT EXISTS post_media("
                "media_id TEXT,"
                "message_id TEXT,"
                "content TEXT,"
                "file_id TEXT,"
                "media_type TEXT,"
                "format_file TEXT,"
                "chat_id TEXT,"
                "mess_first_id TEXT,"
                "flag INTEGER,"
                "FOREIGN KEY(media_id) REFERENCES post_message(media_id))")

    cur.execute("CREATE TABLE IF NOT EXISTS button_states ("
                "media_id TEXT,"
                "button_tg_state TEXT DEFAULT 'off',"
                "button_vk_state TEXT DEFAULT 'off')")

    cur.execute("CREATE TABLE IF NOT EXISTS users_with_rights("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "username TEXT,"
                "user_id TEXT,"
                "rights_post BOOLEAN DEFAULT True,"
                "rights_all BOOLEAN DEFAULT False)")

    cur.execute("CREATE TABLE IF NOT EXISTS samples("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "text TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS users("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "api_id TEXT,"
                "api_hash TEXT,"
                "phone TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS parser_info("
                "channel TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS media_post_vk("
                "media_id TEXT,"
                "media TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS post_info("
                "mess_id TEXT,"
                "source_id TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS groups_vk("
                "group_name TEXT,"
                "group_id TEXT,"
                "flag BOOL DEFAULT True)")

    db.commit()


def add_post_media(
    media_id: str,
    message_id: str = None,
    content: str = None,
    file_id: str = None,
    media_type: str = None,
    format_file: str = None,
    chat_id: str = None,
    mess_first_id: str = None,
    flag: int = 0
):
    # Сначала проверяем, существует ли запись с таким media_id
    cur.execute("SELECT COUNT(*) FROM post_media WHERE media_id = ?", (media_id,))
    exists = cur.fetchone()[0] > 0

    if not exists:
        # Если записи нет, создаем новую
        cur.execute("INSERT INTO post_media (media_id, message_id, content, file_id, media_type, format_file, chat_id, mess_first_id, flag) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (media_id, message_id, content, file_id, media_type, format_file, chat_id, mess_first_id, flag))

    else:
        # Если запись с media_id уже существует, добавляем новую запись
        cur.execute("INSERT INTO post_media (media_id, message_id, content, file_id, media_type, format_file, chat_id, mess_first_id, flag) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (media_id, message_id, content, file_id, media_type, format_file, chat_id, mess_first_id, flag))

    db.commit()


def get_post_media_by_media_id(media_id: str):
    # Выполняем запрос для получения всех записей с указанным media_id
    cur.execute("SELECT * FROM post_media WHERE media_id = ?", (media_id,))
    rows = cur.fetchall()  # Получаем все соответствующие записи
    result = []

    # Формируем список словарей для каждого результата
    for row in rows:
        result.append({
            "media_id": row[0],
            "message_id": row[1],
            "content": row[2],
            "file_id": row[3],
            "media_type": row[4],
            "format_file": row[5],
            "chat_id": row[6],
            "flag": row[8],
            "mess_first_id": row[7]
        })

    return result


def add_signature(title: str) -> None:
    cur.execute("INSERT INTO signatures (title) VALUES (?)", (title,))
    db.commit()


def update_signature(signature_id: int, new_title: str) -> None:
    cur.execute("UPDATE signatures SET title = ? WHERE id = ?", (new_title, signature_id))
    db.commit()


def get_signature_by_id(signature_id: str):
    # Запрос для получения подписи по ID
    cur.execute("SELECT title FROM signatures WHERE id = ?", (signature_id,))
    signature = cur.fetchone()  # Получаем первую строку результата
    return {'title': signature[0]}


def get_all_signatures() -> list[dict]:
    cur.execute("SELECT * FROM signatures")
    rows = cur.fetchall()
    # Преобразуем данные в список словарей для удобства использования
    return [{"id": row[0], "title": row[1]} for row in rows]


def delete_signature(signature_id: int) -> None:
    cur.execute("DELETE FROM signatures WHERE id = ?", (signature_id,))
    db.commit()


def update_post_content(media_id: str, content: str):
    cur.execute("UPDATE post_media SET content = ? WHERE media_id = ?", (content, media_id))
    db.commit()


def update_post_media_entry(media_id: str, file_id: str, media_type: str, format_file: str):

    # Выполняем запрос с переданными значениями
    cur.execute("UPDATE post_media SET file_id = ?, media_type = ?, format_file = ? WHERE media_id = ?",
                (file_id, media_type, format_file, media_id))
    db.commit()


def delete_post_media_entry(file_id: str) -> None:
    cur.execute("DELETE FROM post_media WHERE file_id = ?", (file_id,))
    db.commit()


def delete_post_media_for_media_id(media_id: str) -> None:
    cur.execute("DELETE FROM post_media WHERE media_id = ?", (media_id,))
    db.commit()


def update_file_id(old_file_id: str, new_file_id: str) -> None:
    cur.execute("UPDATE post_media SET file_id = ? WHERE file_id = ?", (new_file_id, old_file_id))
    db.commit()


def update_first_media_content(media_id: str, content: str) -> None:
    cur.execute(
        "UPDATE post_media SET content = ? WHERE media_id = ? AND rowid = (SELECT rowid FROM post_media WHERE media_id = ? ORDER BY rowid ASC LIMIT 1)",
        (content, media_id, media_id)
    )
    db.commit()


def update_flag_signature(media_id: str, flag: int) -> None:
    cur.execute(
        "UPDATE post_media SET flag = ? WHERE media_id = ? AND rowid = (SELECT rowid FROM post_media WHERE media_id = ? ORDER BY rowid ASC LIMIT 1)",
        (flag, media_id, media_id)
    )
    db.commit()


def delete_all_post_media(media_id: str) -> None:
    cur.execute("DELETE FROM post_media WHERE media_id = ?", (media_id,))
    db.commit()


# Функция для добавления записи в колонку publ_time
def add_publ_time_tg(media_id: str, publ_time_tg: str):
    cur.execute("UPDATE post_message SET publ_time_tg = ? WHERE media_id = ?", (publ_time_tg, media_id))
    db.commit()


def add_publ_time_vk(media_id: str, publ_time_vk: str):
    cur.execute("UPDATE post_message SET publ_time_vk = ? WHERE media_id = ?", (publ_time_vk, media_id))
    db.commit()


def get_all_publ_time(media_id: str):
    cur.execute("SELECT publ_time_tg, publ_time_vk FROM post_message WHERE media_id = ?", (media_id,))
    return cur.fetchone()


# Функция для добавления записи в колонку del_time
def add_del_time(media_id: str, del_time: str):
    cur.execute("UPDATE post_message SET del_time = ? WHERE media_id = ?", (del_time, media_id))
    db.commit()


# Функция для добавления записей в обе колонки: publ_time и del_time
def add_publ_and_del_time(media_id: str, publ_time: str, del_time: str):
    cur.execute("UPDATE post_message SET publ_time = ?, del_time = ? WHERE media_id = ?", (publ_time, del_time, media_id))
    db.commit()


def get_all_channel_publish():
    cur.execute("SELECT channel_username, channel_id FROM channel_publish")
    result = []
    for channel in cur.fetchall():
        result.append({
            'channel_username': channel[0],
            'channel_id': channel[1]
        })
    return result


def update_button_states(media_id: str,
                         button_tg_state: str = None,
                         button_vk_state: str = None):
    query = "UPDATE button_states SET "
    params = []

    if button_tg_state is not None:
        query += "button_tg_state = ?, "
        params.append(button_tg_state)

    if button_vk_state is not None:
        query += "button_vk_state = ?, "
        params.append(button_vk_state)

    query = query.rstrip(", ") + " WHERE media_id = ?"
    params.append(media_id)

    cur.execute(query, params)
    db.commit()


def add_button_states(media_id: str):
    cur.execute("""INSERT INTO button_states (media_id, button_tg_state, button_vk_state) VALUES (?, 'off', 'off')""", (media_id,))
    db.commit()


def delete_button_states(media_id: str):
    cur.execute("DELETE FROM button_states WHERE media_id = ?", (media_id,))
    db.commit()


# Функция для получения состояния кнопок
def get_button_states(media_id: str):
    return cur.execute(
        "SELECT button_tg_state, button_vk_state FROM button_states WHERE media_id = ?",
        (media_id,)
    ).fetchone()


def add_message_post(media_id: str):
    del_time = (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d %H:%M:%S")
    cur.execute(
        "INSERT INTO post_message (media_id, del_time) VALUES (?, ?)",
        (media_id, del_time)
    )

    # Сохраняем изменения в базе данных
    db.commit()


def del_message_post(media_id: str):
    cur.execute("DELETE FROM post_message WHERE media_id = ?", (media_id,))
    db.commit()


def get_one_post_message(media_id: str):
    return cur.execute(
        "SELECT media_id, publ_time_tg, publ_time_vk, del_time FROM post_message WHERE media_id = ?",
        (media_id,)).fetchone()


def get_all_post_message():
    cur.execute(
        "SELECT media_id, publ_time_tg, publ_time_vk, del_time FROM post_message")

    rows = cur.fetchall()  # Получаем все соответствующие записи
    result = []

    # Формируем список словарей для каждого результата
    for row in rows:
        result.append({
            "media_id": row[0],
            "publ_time_tg": row[1],
            "publ_time_vk": row[2],
            "del_time": row[3],
        })

    return result


def add_media_post_vk(media_id: str, media: str):
    cur.execute("INSERT INTO media_post_vk (media_id, media) VALUES (?, ?)", (media_id, media))
    db.commit()


def get_all_post_media_vk(media_id: str):
    cur.execute(
        "SELECT media_id, media FROM media_post_vk WHERE media_id = ?", (media_id,))

    rows = cur.fetchall()  # Получаем все соответствующие записи
    result = []

    # Формируем список словарей для каждого результата
    for row in rows:
        result.append({
            "media_id": row[0],
            "media": row[1],
        })
    return result


def delete_media_post_vk(media_id: str):
    # Удаление записи из таблицы по media_id
    cur.execute("DELETE FROM media_post_vk WHERE media_id = ?", (media_id,))
    db.commit()


def get_user_with_rights(user_id):
    return cur.execute(
        "SELECT user_id, username, rights_post, rights_all FROM users_with_rights WHERE user_id = '{}'".format(
            user_id)).fetchone()


def get_users_with_rights():
    return cur.execute(
        "SELECT user_id, username, rights_post, rights_all FROM users_with_rights").fetchall()


def delete_user_with_rights(user_id):
    cur.execute("DELETE FROM users_with_rights WHERE user_id = '{}'".format(user_id))
    db.commit()


def select_chat():
    return cur.execute(
        "SELECT chat_id, chat_username FROM chat").fetchone()


def select_channel_publish(channel_id):
    return cur.execute(
        "SELECT channel_id, channel_username FROM channel_publish WHERE channel_id = '{}'".format(
            channel_id)).fetchone()


def select_channels_publish():
    return cur.execute(
        "SELECT channel_username, channel_id FROM channel_publish").fetchall()


def add_channel_publish(username, channel_id):
    cur.execute(
        "INSERT INTO channel_publish (channel_username, channel_id) VALUES ('{}', '{}')".format(username, channel_id)
    )


def delete_channel_publish(channel_id):
    cur.execute("DELETE FROM channel_publish WHERE channel_id = '{}'".format(channel_id))
    db.commit()


def add_sample(text):
    cur.execute(
        "INSERT INTO samples (text) VALUES ('{}')".format(text)
    )
    db.commit()


def delete_sample(sample_id):
    cur.execute("DELETE FROM samples WHERE id = '{}'".format(sample_id))
    db.commit()


def select_samples():
    return cur.execute(
        "SELECT id, text FROM samples").fetchall()


def select_sample(sample_id):
    return cur.execute(
        "SELECT text FROM samples WHERE id = '{}'".format(sample_id)).fetchone()


def add_update_chat(username, chat_id):
    if not select_chat():
        cur.execute(
            "INSERT INTO chat (chat_username, chat_id) VALUES ('{}', '{}')".format(username, chat_id)
        )
    else:
        cur.execute(
            "UPDATE chat SET chat_username = '{}', chat_id = '{}'".format(username, chat_id))
    db.commit()


def add_users_with_rights_post(username, user_id):
    cur.execute(
        "INSERT INTO users_with_rights (username, user_id) VALUES ('{}', '{}')".format(username, user_id)
    )
    db.commit()


def update_users_with_rights_all(user_id):
    cur.execute(
        "UPDATE users_with_rights SET rights_all = TRUE WHERE user_id = '{}'".format(user_id))
    db.commit()


def update_users_del_rights_all(user_id):
    cur.execute(
        "UPDATE users_with_rights SET rights_all = FALSE WHERE user_id = '{}'".format(user_id))
    db.commit()


def get_sources():
    return cur.execute(
        "SELECT id, title FROM sources").fetchall()


def get_source(title):
    return cur.execute(
        "SELECT title FROM sources WHERE title = '{}'".format(title)).fetchone()


def add_source(title):
    cur.execute(
        "INSERT INTO sources (title) VALUES ('{}')".format(title)
    )
    db.commit()


def del_source(source_id):
    cur.execute("DELETE FROM sources WHERE id = '{}'".format(source_id))

    db.commit()


def add_parser_info(channel):
    cur.execute(
        "INSERT INTO parser_info (channel) VALUES ('{}')".format(channel)
    )
    db.commit()


def get_parser_info(channel):
    return cur.execute(
        "SELECT channel FROM parser_info WHERE channel = '{}'".format(channel)).fetchone()


def get_all_parser_info():
    return cur.execute(
        "SELECT channel FROM parser_info").fetchall()


def delete_parser_info(channel):
    cur.execute("DELETE FROM parser_info WHERE channel = '{}'".format(channel))
    db.commit()


def delete_all_parser_info():
    cur.execute("DELETE FROM parser_info")  # Удаляет все записи из таблицы
    db.commit()



def add_post_info(mess_id, source_id):
    cur.execute(
        "INSERT INTO post_info (mess_id, source_id) VALUES (?, ?)",
        (mess_id, source_id)
    )
    db.commit()


def get_mess_id(mess_id, source_id):
    query = "SELECT mess_id,source_id FROM post_info WHERE mess_id = ? AND source_id = ?"
    return cur.execute(query, (mess_id, source_id)).fetchone()


def select_user():
    return cur.execute(
        "SELECT api_id, api_hash, phone FROM users").fetchone()


def delete_all_users_bot():
    cur.execute("DELETE FROM users")
    db.commit()


def select_user_with_param(api_id):
    return cur.execute(
        "SELECT api_id, api_hash, phone FROM users WHERE api_id = '{}'".format(api_id)).fetchone()


def add_user(api_id, api_hash, phone):
    cur.execute(
        "INSERT INTO users (api_id, api_hash, phone) VALUES ('{}', '{}', '{}')".format(api_id, api_hash, phone)
    )
    db.commit()


# 25860381 d51fab97d193da6c77498f039d3af352 +7 931 974 3864
def update_user(api_id, api_hash, phone):
    cur.execute(
        "DELETE FROM users"
    )
    db.commit()
    cur.execute(
        "INSERT INTO users (api_id, api_hash, phone) VALUES ('{}', '{}', '{}')".format(api_id, api_hash, phone)
    )
    db.commit()


def add_who_worked(user_id, caption, mess_id):
    cur.execute(
        "INSERT INTO who_worked (user_id, caption, mess_id) VALUES (?, ?, ?)",
        (user_id, caption, mess_id)
    )
    db.commit()


def select_who_worked(mess_id: str):
    return cur.execute(
        "SELECT user_id, caption, mess_id FROM who_worked WHERE mess_id = ?",
        (mess_id,)).fetchone()


def delete_who_worked(mess_id):
    cur.execute(
        "DELETE FROM who_worked WHERE mess_id = ?", (mess_id,)
    )
    db.commit()


def add_group_vk(group_name: str, group_id: str, flag: bool = True):
    cur.execute(
        "INSERT INTO groups_vk (group_name, group_id, flag) VALUES (?, ?, ?)",
        (group_name, group_id, flag)
    )
    db.commit()


def update_flag_vk(group_id: str, flag_value: int = True):
    cur.execute(
        "UPDATE groups_vk SET flag = ? WHERE group_id = ?",
        (flag_value, group_id)
    )
    db.commit()


def select_groups_vk():
    return cur.execute(
        "SELECT group_name, group_id, flag FROM groups_vk").fetchall()


def select_group_vk(group_id: str):
    return cur.execute(
        "SELECT group_name, group_id, flag FROM groups_vk WHERE group_id = ?", (group_id,)).fetchone()


def delete_group_vk(group_id: str):
    cur.execute(
        "DELETE FROM groups_vk WHERE group_id = ?", (group_id,)
    )
    db.commit()
