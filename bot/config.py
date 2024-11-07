import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = "7662625241:AAGzjJfgh2GjWRuU1kQTw1f561eqgTxhupM"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(
    parse_mode=ParseMode.HTML),
          )


dp = Dispatcher(bot=bot, storage=MemoryStorage())
