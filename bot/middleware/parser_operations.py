import asyncio
import logging
import os
from collections import deque
from collections.abc import Coroutine

from aiogram.utils.markdown import hlink
from pyrogram import Client

from database.clients import clients
from database.db import get_sources, get_parser_info, delete_parser_info, select_chat, get_all_parser_info, \
    add_post_info, get_mess_id


def get_all_sources():
    data = [f"{get_source_status(sou[1])} {hlink(sou[1], url=f'https://t.me/{sou[1]}')}\n" for sou in
            get_sources()]
    return "".join(data)


async def check_channel(client: Client, username):
    try:
        await client.get_chat(username)
        return True
    except:
        return False


def get_sources_ids():
    ids = [sou[0] for sou in get_sources()]
    return ids


def stop_parsers(sources):
    for _id, title in sources:
        if get_parser_info(title):
            delete_parser_info(title)


def delete_session(api_id):
    if os.path.exists(f"{api_id}.session-journal"):
        client: Client = clients.get("client")
        client.stop()
    if os.path.exists(f"{api_id}.session"):
        os.remove(f"{api_id}.session")


def get_source_status(title):
    source = get_parser_info(title)
    if source:
        return "✅"
    else:
        return "❌"


async def parser():
    processed_messages = deque(maxlen=40)
    client: Client = clients.get("client")
    chat_id, username = select_chat()
    while True:
        ids = get_all_parser_info()
        if not ids:
            await asyncio.sleep(10)
            continue
        else:
            for source_id in ids:
                source_id = source_id[0]
                last_post = client.get_chat_history(source_id, limit=1)
                async for mess in last_post:
                    if not get_mess_id(mess_id=mess.id, source_id=source_id):
                        try:
                            if mess.media_group_id:
                                if mess.id in processed_messages:
                                    continue
                                processed_messages.append(mess.id)
                                try:
                                    await client.forward_messages(
                                        chat_id=username,
                                        from_chat_id=source_id,
                                        message_ids=mess.id,
                                    )
                                except Exception:
                                    await client.copy_media_group(
                                        chat_id=username,
                                        from_chat_id=source_id,
                                        message_id=mess.id,
                                    )
                            else:
                                if mess.id in processed_messages:
                                    continue
                                await client.forward_messages(
                                    chat_id=username,
                                    from_chat_id=source_id,
                                    message_ids=mess.id,
                                )

                            add_post_info(mess_id=mess.id, source_id=source_id)
                        except Exception as ex:
                            logging.error(f"Ошибка в парсере: {ex}")

            await asyncio.sleep(60)


class TaskManager:
    _tasks = {}
    PARSER_NAME = "parser_userbot"

    @classmethod
    def start(cls) -> None:
        task = cls._tasks.get(cls.PARSER_NAME)
        if task and not task.done():
            return
        cls._tasks[cls.PARSER_NAME] = asyncio.create_task(parser())

    @classmethod
    def stop(cls) -> None:
        task = cls._tasks.get(cls.PARSER_NAME)
        if task and not task.done():
            task.cancel()
