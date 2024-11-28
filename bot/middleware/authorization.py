import asyncio
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, TelegramObject, CallbackQuery

from bot.config import ADMIN

from bot.middleware.admin_operations import get_users_id_with_rights, get_users_id_with_all_rights


class AuthorizationMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        authorization = get_flag(data, "authorization")
        if authorization is not None:
            if isinstance(event, Message):
                if int(event.chat.id) == int(ADMIN):
                    return await handler(event, data)
                elif authorization.get("post_rights") and (str(event.chat.id) in get_users_id_with_rights()):
                    return await handler(event, data)
                elif authorization.get("all_rights") and (str(event.chat.id) in get_users_id_with_all_rights()):
                    return await handler(event, data)
                else:
                    bot_mess = await event.answer("У вас нет прав")
                    await asyncio.sleep(3)
                    await bot_mess.delete()
                    return await event.delete()
            elif isinstance(event, CallbackQuery):
                if int(event.message.chat.id) == int(ADMIN):
                    return await handler(event, data)
                elif authorization.get("all_rights") and (str(event.message.chat.id) in get_users_id_with_all_rights()):
                    return await handler(event, data)
                elif authorization.get("post_rights") and (str(event.message.chat.id) in get_users_id_with_rights()):
                    return await handler(event, data)
                else:
                    await event.answer("У вас нет прав")

        else:
            return await handler(event, data)
