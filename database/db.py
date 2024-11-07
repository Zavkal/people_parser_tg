import sqlite3 as sq
db = sq.connect("../database/db_bot.db")
cur = db.cursor()


async def start_db():
    cur.execute("CREATE TABLE IF NOT EXISTS who_worked("
                "user_id TEXT,"
                "caption TEXT,"
                "file_id TEXT)")


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
                "flag INTEGER,"
                "FOREIGN KEY(media_id) REFERENCES post_message(media_id))")


    cur.execute("CREATE TABLE IF NOT EXISTS button_states ("
                    "media_id TEXT,"
                    "button_tg_state TEXT DEFAULT 'off',"
                    "button_vk_state TEXT DEFAULT 'off')")


    db.commit()


def add_post_media(
    media_id: str,
    message_id: str = None,
    content: str = None,
    file_id: str = None,
    media_type: str = None,
    format_file: str = None,
    chat_id: str = None,
    flag: int = 0
):
    # Сначала проверяем, существует ли запись с таким media_id
    cur.execute("SELECT COUNT(*) FROM post_media WHERE media_id = ?", (media_id,))
    exists = cur.fetchone()[0] > 0

    if not exists:
        # Если записи нет, создаем новую
        cur.execute("INSERT INTO post_media (media_id, message_id, content, file_id, media_type, format_file, chat_id, flag) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (media_id, message_id, content, file_id, media_type, format_file, chat_id, flag))

    else:
        # Если запись с media_id уже существует, добавляем новую запись
        cur.execute("INSERT INTO post_media (media_id, message_id, content, file_id, media_type, format_file, chat_id, flag) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (media_id, message_id, content, file_id, media_type, format_file, chat_id, flag))

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
            "flag": row[7]
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


def add_message_post(media_id: str):
    cur.execute("INSERT INTO post_message (media_id) VALUES (?)", (media_id,))

    db.commit()


# Функция для получения состояния кнопок
def get_button_states(media_id: str):
    return cur.execute(
        "SELECT button_tg_state, button_vk_state FROM button_states WHERE media_id = ?",
        (media_id,)
    ).fetchone()

