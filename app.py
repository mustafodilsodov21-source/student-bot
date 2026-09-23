
import asyncio
import logging
import os
import sys

from loader import bot, db, dp
from handlers.users.start import router as user_router
from handlers.admin.panel import router as admin_router
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


# ============================================================
# LOGGING
# ============================================================

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            "logs/bot.log",
            encoding="utf-8",
        ),
    ],
)

logger = logging.getLogger("student_bot")


# ============================================================
# APPLICATION
# ============================================================

async def main() -> None:
    logger.info("Starting Student Bot...")

    try:
        # ----------------------------------------------------
        # DATABASE
        # ----------------------------------------------------
        db.create_table_students()
        logger.info("Database initialized")

        # ----------------------------------------------------
        # ROUTERS
        # ----------------------------------------------------
        dp.include_router(user_router)
        dp.include_router(admin_router)

        logger.info("Routers registered")

        # ----------------------------------------------------
        # BOT COMMANDS
        # ----------------------------------------------------
        await set_default_commands()
        logger.info("Bot commands configured")

        # ----------------------------------------------------
        # STARTUP NOTIFICATION
        # ----------------------------------------------------
        await on_startup_notify()

        logger.info("Student Bot is running")

        # ----------------------------------------------------
        # POLLING
        # ----------------------------------------------------
        await dp.start_polling(bot)

    except Exception:
        logger.exception("Fatal application error")
        raise

    finally:
        await bot.session.close()
        logger.info("Bot session closed")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        logger.info("Application stopped by user")

