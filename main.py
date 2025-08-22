import asyncio

from database.db import start_db
from bot.middleware.authorization import AuthorizationMiddleware
from bot.config import bot, dp

from bot.logger import logger
from bot.handlers.start_handler import router as start_router
from bot.handlers.base_post_work_handler import router as base_post_work_router
from bot.handlers.send_post_handler import router as send_post_router
from bot.handlers.change_post_handler import router as change_post_router
from bot.handlers.pars_message_chat import router as pars_message_chat

from bot.handlers.send_to_tg_handler import router as send_to_tg_router
from bot.handlers.send_to_vk_handler import router as send_to_vk_router
from bot.handlers.admin import router as admin_panel
from bot.handlers.parser import router as parser_router
from bot.handlers.user_bot import router as user_bot
from bot.handlers.queue import router as queue

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '')))


async def main() -> None:
    await start_db()
    logger.info("[Запуск бота] Бот запущен ассинхронно!")
    dp.include_routers(
        start_router,
        base_post_work_router,
        send_post_router,
        change_post_router,
        send_to_tg_router,
        send_to_vk_router,
        pars_message_chat,
        admin_panel,
        parser_router,
        user_bot,
        queue,
    )
    dp.callback_query.middleware(AuthorizationMiddleware())
    dp.message.middleware(AuthorizationMiddleware())
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
