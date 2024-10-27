import asyncio

from config import bot, dp
from database.db import start_db
from logger import logger
from handlers.start_handler import router as start_router
from handlers.base_post_work_handler import router as base_post_work_router
from handlers.send_post_handler import router as send_post_router
from handlers.change_post_handler import router as change_post_router
from handlers.pars_message_chat import router as pars_message_chat

from handlers.send_to_tg_handler import router as send_to_tg_router
from handlers.send_to_vk_handler import router as send_to_vk_router


async def main() -> None:
    logger.info("[Запуск бота] Бот запущен ассинхронно!")
    dp.include_routers(
        start_router,
        base_post_work_router,
        send_post_router,
        change_post_router,
        send_to_tg_router,
        send_to_vk_router,
        pars_message_chat,
    )
    await start_db()
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
