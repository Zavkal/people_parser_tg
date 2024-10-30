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
                "publ_time TEXT)")


    # Добавил бд с путями до файлов с привязкой по post_id
    cur.execute("CREATE TABLE IF NOT EXISTS post_media("
                "media_id TEXT,"
                "message_id TEXT,"
                "content TEXT,"
                "file_id TEXT,"
                "media_type TEXT,"
                "format_file TEXT,"
                "user_id TEXT,"
                "FOREIGN KEY(media_id) REFERENCES post_message(media_id))")


    # Добавил Состоянии кнопок для упрощения своей работы.
    cur.execute("CREATE TABLE IF NOT EXISTS button_states ("
                "post_id TEXT,"
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
    user_id: str = None
):
    # Сначала проверяем, существует ли запись с таким media_id
    cur.execute("SELECT COUNT(*) FROM post_media WHERE media_id = ?", (media_id,))
    exists = cur.fetchone()[0] > 0

    if not exists:
        # Если записи нет, создаем новую
        cur.execute("INSERT INTO post_media (media_id, message_id, content, file_id, media_type, format_file, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (media_id, message_id, content, file_id, media_type, format_file, user_id))
        cur.execute("INSERT INTO post_message (media_id) VALUES (?)", (media_id,))
    else:
        # Если запись с media_id уже существует, добавляем новую запись
        cur.execute("INSERT INTO post_media (media_id, message_id, content, file_id, media_type, format_file, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (media_id, message_id, content, file_id, media_type, format_file, user_id))

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
            "user_id": row[6]
        })

    return result


def add_signature(title: str) -> None:
    cur.execute("INSERT INTO signatures (title) VALUES (?)", (title,))
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

