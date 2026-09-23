
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_edit_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="👤 Имя"),
                KeyboardButton(text="📝 Фамилия")
            ],
            [
                KeyboardButton(text="🎂 Возраст"),
                KeyboardButton(text="📱 Телефон")
            ],
            [
                KeyboardButton(text="⬅️ Назад")
            ]
        ],
        resize_keyboard=True
    )

