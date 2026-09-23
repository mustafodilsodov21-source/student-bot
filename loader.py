
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy

from data import config
from middlewares.throttling import ManualThrottlingMiddleware
from utils.db_api.sqlite import Database


# ============================================================
# BOT
# ============================================================

bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)


# ============================================================
# DISPATCHER
# ============================================================

storage = MemoryStorage()

dp = Dispatcher(
    storage=storage,
    fsm_strategy=FSMStrategy.CHAT
)


# ============================================================
# MIDDLEWARES
# ============================================================

dp.message.middleware(
    ManualThrottlingMiddleware()
)


# ============================================================
# DATABASE
# ============================================================

db = Database(
    path_to_db="data/students.db"
)
