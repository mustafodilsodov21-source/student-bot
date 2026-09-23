
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """
    Build the main reply keyboard.

    Regular users receive only student-related actions.
    Administrators additionally receive admin actions.
    """

    keyboard = [
        [
            KeyboardButton(
                text="📝 Регистрация",
            ),
            KeyboardButton(
                text="👤 Мои данные",
            ),
        ],
        [
            KeyboardButton(
                text="✏️ Изменить данные",
            ),
            KeyboardButton(
                text="🗑 Удалить данные",
            ),
        ],
    ]

    if is_admin:
        keyboard.extend(
            [
                [
                    KeyboardButton(
                        text="👥 Все студенты",
                    ),
                ],
                [
                    KeyboardButton(
                        text="📢 Реклама",
                    ),
                    KeyboardButton(
                        text="📊 Статистика",
                    ),
                ],
            ]
        )

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
    )

