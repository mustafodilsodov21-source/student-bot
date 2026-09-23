
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# ============================================================
# MAIN ADMIN PANEL
# ============================================================

def admin_keyboard() -> InlineKeyboardMarkup:
    """
    Main administrator panel.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Реклама",
                    callback_data="admin_ad",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👥 Пользователи",
                    callback_data="admin_users",
                ),
                InlineKeyboardButton(
                    text="📊 Статистика",
                    callback_data="admin_stats",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📨 История рассылок",
                    callback_data="admin_history",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⚙️ Настройки",
                    callback_data="admin_settings",
                ),
            ],
        ]
    )


# ============================================================
# ADVERTISING MENU
# ============================================================

def advertising_keyboard() -> InlineKeyboardMarkup:
    """
    Advertising management menu.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Создать рассылку",
                    callback_data="ad_create",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📊 Последняя рассылка",
                    callback_data="ad_last",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="admin_back",
                ),
            ],
        ]
    )


# ============================================================
# AD CREATION
# ============================================================

def ad_back_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard displayed while creating an advertisement.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="ad_back",
                ),
            ],
        ]
    )


# ============================================================
# AD CONFIRMATION
# ============================================================

def ad_confirm_keyboard() -> InlineKeyboardMarkup:
    """
    Advertisement confirmation keyboard.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Разослать",
                    callback_data="ad_send",
                ),
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="ad_cancel",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="ad_back",
                ),
            ],
        ]
    )


# ============================================================
# AFTER ADVERTISEMENT
# ============================================================

def ad_finished_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard displayed after advertisement delivery.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Новая рассылка",
                    callback_data="admin_ad",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔙 В админ-панель",
                    callback_data="admin_back",
                ),
            ],
        ]
    )

