
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def admin_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Reply keyboard for administrator.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📢 Реклама",
                ),
            ],
            [
                KeyboardButton(
                    text="📊 Статистика",
                ),
                KeyboardButton(
                    text="👥 Пользователи",
                ),
            ],
            [
                KeyboardButton(
                    text="📨 История",
                ),
                KeyboardButton(
                    text="⚙️ Настройки",
                ),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

