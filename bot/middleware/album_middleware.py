import asyncio
from typing import Any, Dict, Union
from aiogram import BaseMiddleware
from aiogram.types import Message


class AlbumMiddleware(BaseMiddleware):
    def __init__(self, latency: Union[int, float] = 0.1):
        self.latency = latency
        self.album_data = {}
        self.locks = {}  # Для предотвращения гонок данных

    async def collect_album_messages(self, event: Message):
        """
        Собираем сообщения в альбом.
        """
        media_group_id = event.media_group_id

        # Если замка для этой группы еще нет, создаем
        if media_group_id not in self.locks:
            self.locks[media_group_id] = asyncio.Lock()

        # Блокируем доступ к группе сообщений
        async with self.locks[media_group_id]:
            if media_group_id not in self.album_data:
                self.album_data[media_group_id] = {"messages": []}
            self.album_data[media_group_id]["messages"].append(event)

        # Возвращаем текущее количество сообщений
        return len(self.album_data[media_group_id]["messages"])

    async def __call__(self, handler, event: Message, data: Dict[str, Any]) -> Any:
        """
        Основная логика миддлвара.
        """
        media_group_id = event.media_group_id

        # Если сообщение не относится к альбому, передаем его сразу
        if not media_group_id:
            return await handler(event, data)

        # Сбор сообщений альбома
        total_before = await self.collect_album_messages(event)

        # Ждем заданную задержку
        await asyncio.sleep(self.latency)

        # Проверяем, добавились ли новые сообщения за это время
        async with self.locks[media_group_id]:
            total_after = len(self.album_data[media_group_id]["messages"])
            if total_before != total_after:
                return  # Новые сообщения были добавлены

            # Сортируем сообщения и добавляем их в данные
            album_messages = self.album_data[media_group_id]["messages"]
            album_messages.sort(key=lambda x: x.message_id)
            data["album"] = album_messages

            # Удаляем данные альбома и замок
            del self.album_data[media_group_id]
            del self.locks[media_group_id]

        # Передаем управление обработчику
        return await handler(event, data)
