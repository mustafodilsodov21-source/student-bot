
from aiogram.types import BotCommand

from loader import bot


async def set_default_commands() -> None:
    """
    Configure default Telegram bot commands.
    """

    commands = [
        BotCommand(
            command="start",
            description="Запустить бота",
        ),
        BotCommand(
            command="stats",
            description="Статистика",
        ),
        BotCommand(
            command="cancel",
            description="Отменить действие",
        ),
    ]

    await bot.set_my_commands(commands)

