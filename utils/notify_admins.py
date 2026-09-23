
import logging

from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from data.config import ADMIN_IDS
from loader import bot


logger = logging.getLogger(__name__)


async def on_startup_notify() -> None:
    """
    Notify all configured administrators that the bot has started.
    """

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text="🟢 <b>Student Bot запущен</b>",
            )

            logger.info(
                "Startup notification sent | admin=%s",
                admin_id,
            )

        except TelegramForbiddenError:
            logger.warning(
                "Startup notification blocked | admin=%s",
                admin_id,
            )

        except TelegramBadRequest:
            logger.warning(
                "Telegram rejected startup notification | admin=%s",
                admin_id,
                exc_info=True,
            )

        except Exception:
            logger.exception(
                "Unexpected startup notification error | admin=%s",
                admin_id,
            )

