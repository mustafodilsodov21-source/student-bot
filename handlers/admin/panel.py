import asyncio
import logging

from aiogram import F, Router
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
)
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from data.config import ADMIN_IDS
from keyboards.admin.main import (
    ad_back_keyboard,
    ad_confirm_keyboard,
    ad_finished_keyboard,
    admin_keyboard,
    advertising_keyboard,
)
from loader import bot, db
from states.main import AdminStates


router = Router()

logger = logging.getLogger(__name__)


# =========================================================
# ADMIN ACCESS
# =========================================================

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


async def deny_access(
    callback: CallbackQuery,
) -> None:
    await callback.answer(
        "❌ У вас нет доступа.",
        show_alert=True,
    )


# =========================================================
# ADVERTISING — REPLY BUTTON
# =========================================================

@router.message(F.text == "📢 Реклама")
async def advertising_button(
    message: Message,
) -> None:
    if not is_admin(message.from_user.id):
        return

    await message.answer(
        "📢 <b>Рекламная рассылка</b>\n\n"
        "Выберите действие:",
        reply_markup=advertising_keyboard(),
    )


# =========================================================
# ADVERTISING — INLINE MENU
# =========================================================

@router.callback_query(F.data == "admin_ad")
async def advertising_menu(
    callback: CallbackQuery,
) -> None:
    if not is_admin(callback.from_user.id):
        await deny_access(callback)
        return

    text = (
        "📢 <b>Рекламная рассылка</b>\n\n"
        "Выберите действие:"
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=advertising_keyboard(),
        )
    except TelegramBadRequest as error:
        if "message is not modified" not in str(error):
            raise

    await callback.answer()


# =========================================================
# CREATE ADVERTISEMENT
# =========================================================

@router.callback_query(F.data == "ad_create")
async def start_ad(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if not is_admin(callback.from_user.id):
        await deny_access(callback)
        return

    await state.set_state(
        AdminStates.waiting_for_ad,
    )

    text = (
        "📢 <b>Создание рассылки</b>\n\n"
        "Отправьте сообщение, которое хотите разослать.\n\n"
        "<b>Поддерживается:</b>\n"
        "📝 Текст\n"
        "🖼 Фото\n"
        "🎥 Видео\n"
        "📄 Документы\n\n"
        "После отправки вы увидите предпросмотр."
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=ad_back_keyboard(),
        )
    except TelegramBadRequest as error:
        if "message is not modified" not in str(error):
            raise

    await callback.answer()


# =========================================================
# RECEIVE ADVERTISEMENT
# =========================================================

@router.message(AdminStates.waiting_for_ad)
async def receive_ad(
    message: Message,
    state: FSMContext,
) -> None:
    if not is_admin(message.from_user.id):
        return

    message_text = (
        message.text
        or message.caption
        or "Медиа-сообщение"
    )

    await state.update_data(
        message_id=message.message_id,
        chat_id=message.chat.id,
        message_text=message_text,
    )

    await state.set_state(
        AdminStates.confirming_ad,
    )

    await message.answer(
        "👁 <b>Предпросмотр рассылки</b>\n\n"
        "Ваше сообщение:"
    )

    await message.copy_to(
        chat_id=message.chat.id,
    )

    await message.answer(
        "━━━━━━━━━━━━━━━━━━\n"
        "Всё выглядит правильно?",
        reply_markup=ad_confirm_keyboard(),
    )


# =========================================================
# BACK FROM ADVERTISEMENT
# =========================================================

@router.callback_query(F.data == "ad_back")
async def ad_back(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if not is_admin(callback.from_user.id):
        await deny_access(callback)
        return

    await state.clear()

    text = (
        "📢 <b>Рекламная рассылка</b>\n\n"
        "Выберите действие:"
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=advertising_keyboard(),
        )
    except TelegramBadRequest as error:
        if "message is not modified" not in str(error):
            raise

    await callback.answer()


# =========================================================
# CANCEL ADVERTISEMENT
# =========================================================

@router.callback_query(F.data == "ad_cancel")
async def cancel_ad(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if not is_admin(callback.from_user.id):
        await deny_access(callback)
        return

    await state.clear()

    text = (
        "📢 <b>Рекламная рассылка</b>\n\n"
        "❌ <b>Рассылка отменена.</b>\n\n"
        "Выберите действие:"
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=advertising_keyboard(),
        )
    except TelegramBadRequest as error:
        if "message is not modified" not in str(error):
            raise

    await callback.answer(
        "Рассылка отменена.",
    )


# =========================================================
# SEND ADVERTISEMENT
# =========================================================

@router.callback_query(F.data == "ad_send")
async def send_ad(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if not is_admin(callback.from_user.id):
        await deny_access(callback)
        return

    data = await state.get_data()

    message_id = data.get("message_id")
    chat_id = data.get("chat_id")
    message_text = data.get(
        "message_text",
        "Медиа-сообщение",
    )

    if not message_id or not chat_id:
        await state.clear()

        try:
            await callback.message.edit_text(
                "❌ <b>Ошибка</b>\n\n"
                "Не удалось найти рекламное сообщение.",
                reply_markup=advertising_keyboard(),
            )
        except TelegramBadRequest as error:
            if "message is not modified" not in str(error):
                raise

        await callback.answer()
        return

    telegram_ids = db.get_all_telegram_ids()

    if not telegram_ids:
        await state.clear()

        try:
            await callback.message.edit_text(
                "⚠️ <b>Нет получателей</b>\n\n"
                "В базе пока нет зарегистрированных "
                "пользователей.",
                reply_markup=advertising_keyboard(),
            )
        except TelegramBadRequest as error:
            if "message is not modified" not in str(error):
                raise

        await callback.answer()
        return

    total = len(telegram_ids)

    try:
        await callback.message.edit_text(
            "📢 <b>Рассылка запущена</b>\n\n"
            f"👥 Получателей: <b>{total}</b>\n"
            "⏱ Интервал: 0.4 секунды\n\n"
            "Пожалуйста, подождите...",
        )
    except TelegramBadRequest as error:
        if "message is not modified" not in str(error):
            raise

    sent = 0
    failed = 0

    for telegram_id in telegram_ids:
        try:
            await bot.copy_message(
                chat_id=telegram_id,
                from_chat_id=chat_id,
                message_id=message_id,
            )

            sent += 1

        except TelegramForbiddenError:
            failed += 1

            logger.warning(
                "Advertisement blocked by user | target=%s",
                telegram_id,
            )

        except TelegramBadRequest:
            failed += 1

            logger.warning(
                "Advertisement rejected by Telegram | target=%s",
                telegram_id,
                exc_info=True,
            )

        except Exception:
            failed += 1

            logger.exception(
                "Unexpected advertisement error | target=%s",
                telegram_id,
            )

        await asyncio.sleep(0.4)

    # =====================================================
    # SAVE ADVERTISEMENT HISTORY
    # =====================================================

    db.add_advertisement(
        admin_id=callback.from_user.id,
        message_text=message_text,
        total_users=total,
        successful_sends=sent,
        failed_sends=failed,
    )

    await state.clear()

    logger.info(
        "Admin %s | advertisement completed | "
        "total=%s | sent=%s | failed=%s",
        callback.from_user.id,
        total,
        sent,
        failed,
    )

    await callback.message.answer(
        "📊 <b>Рассылка завершена</b>\n\n"
        f"👥 Всего: <b>{total}</b>\n"
        f"✅ Успешно: <b>{sent}</b>\n"
        f"❌ Ошибок: <b>{failed}</b>",
        reply_markup=ad_finished_keyboard(),
    )

    await callback.answer(
        "Готово",
    )


# =========================================================
# LAST ADVERTISEMENT
# =========================================================

@router.callback_query(F.data == "ad_last")
async def last_advertisement(
    callback: CallbackQuery,
) -> None:
    if not is_admin(callback.from_user.id):
        await deny_access(callback)
        return

    advertisement = db.get_last_advertisement()

    if advertisement is None:
        text = (
            "📊 <b>Последняя рассылка</b>\n\n"
            "📭 Рассылок пока не было."
        )

        try:
            await callback.message.edit_text(
                text,
                reply_markup=advertising_keyboard(),
            )
        except TelegramBadRequest as error:
            if "message is not modified" not in str(error):
                raise

        await callback.answer()
        return

    message_text = advertisement["message_text"]

    if not message_text:
        message_text = "Медиа-сообщение"

    if len(message_text) > 500:
        message_text = (
            message_text[:500]
            + "..."
        )

    text = (
        "📊 <b>Последняя рассылка</b>\n\n"
        f"🆔 ID: <code>{advertisement['id']}</code>\n"
        f"📅 Дата: <code>{advertisement['created_at']}</code>\n\n"
        "📝 <b>Сообщение:</b>\n"
        f"{message_text}\n\n"
        "📈 <b>Результат:</b>\n"
        f"👥 Получателей: "
        f"<b>{advertisement['total_users']}</b>\n"
        f"✅ Успешно: "
        f"<b>{advertisement['successful_sends']}</b>\n"
        f"❌ Ошибок: "
        f"<b>{advertisement['failed_sends']}</b>"
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=advertising_keyboard(),
        )
    except TelegramBadRequest as error:
        if "message is not modified" not in str(error):
            raise

    logger.info(
        "Admin %s | action=last_advertisement | ad_id=%s",
        callback.from_user.id,
        advertisement["id"],
    )

    await callback.answer()


# =========================================================
# USERS
# =========================================================

@router.callback_query(F.data == "admin_users")
async def admin_users(
    callback: CallbackQuery,
) -> None:
    if not is_admin(callback.from_user.id):
        await deny_access(callback)
        return

    students = db.get_all_students()

    if not students:
        text = (
            "👥 <b>Пользователи</b>\n\n"
            "📭 В базе пока нет "
            "зарегистрированных студентов."
        )

        try:
            await callback.message.edit_text(
                text,
                reply_markup=admin_keyboard(),
            )
        except TelegramBadRequest as error:
            if "message is not modified" not in str(error):
                raise

        await callback.answer()
        return

    text = (
        "👥 <b>Пользователи</b>\n\n"
        f"Всего зарегистрировано: "
        f"<b>{len(students)}</b>\n\n"
    )

    for student in students[:20]:
        text += (
            f"🆔 <code>{student['telegram_id']}</code>\n"
            f"👤 {student['first_name']} "
            f"{student['last_name']}\n"
            f"🎂 {student['age']}\n"
            f"📱 {student['phone']}\n"
            "━━━━━━━━━━━━━━\n"
        )

    if len(students) > 20:
        text += (
            f"\nПоказаны первые 20 "
            f"из {len(students)} пользователей."
        )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=admin_keyboard(),
        )
    except TelegramBadRequest as error:
        if "message is not modified" not in str(error):
            raise

    await callback.answer()


# =========================================================
# STATISTICS — INLINE BUTTON
# =========================================================

@router.callback_query(F.data == "admin_stats")
async def admin_stats(
    callback: CallbackQuery,
) -> None:
    if not is_admin(callback.from_user.id):
        await deny_access(callback)
        return

    count = db.count_students()

    text = (
        "📊 <b>Статистика</b>\n\n"
        f"👥 Зарегистрированных студентов: "
        f"<b>{count}</b>"
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=admin_keyboard(),
        )
    except TelegramBadRequest as error:
        if "message is not modified" not in str(error):
            raise

    logger.info(
        "Admin %s | action=admin_stats | students=%s",
        callback.from_user.id,
        count,
    )

    await callback.answer()


# =========================================================
# ADVERTISEMENT HISTORY
# =========================================================

@router.callback_query(F.data == "admin_history")
async def admin_history(
    callback: CallbackQuery,
) -> None:
    if not is_admin(callback.from_user.id):
        await deny_access(callback)
        return

    advertisements = db.get_advertisement_history(
        limit=20,
    )

    if not advertisements:
        text = (
            "📨 <b>История рассылок</b>\n\n"
            "📭 Рассылок пока не было."
        )

        try:
            await callback.message.edit_text(
                text,
                reply_markup=admin_keyboard(),
            )
        except TelegramBadRequest as error:
            if "message is not modified" not in str(error):
                raise

        await callback.answer()
        return

    text = (
        "📨 <b>История рассылок</b>\n\n"
        f"Всего показано: "
        f"<b>{len(advertisements)}</b>\n\n"
    )

    for advertisement in advertisements:
        message_text = advertisement["message_text"]

        if not message_text:
            message_text = "Медиа-сообщение"

        if len(message_text) > 80:
            message_text = (
                message_text[:80]
                + "..."
            )

        text += (
            f"🆔 <b>#{advertisement['id']}</b>\n"
            f"📅 {advertisement['created_at']}\n"
            f"📝 {message_text}\n"
            f"👥 Получателей: "
            f"<b>{advertisement['total_users']}</b>\n"
            f"✅ Успешно: "
            f"<b>{advertisement['successful_sends']}</b>\n"
            f"❌ Ошибок: "
            f"<b>{advertisement['failed_sends']}</b>\n"
            "━━━━━━━━━━━━━━\n"
        )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=admin_keyboard(),
        )
    except TelegramBadRequest as error:
        if "message is not modified" not in str(error):
            raise

    logger.info(
        "Admin %s | action=admin_history | count=%s",
        callback.from_user.id,
        len(advertisements),
    )

    await callback.answer()


# =========================================================
# SETTINGS
# =========================================================

@router.callback_query(F.data == "admin_settings")
async def admin_settings(
    callback: CallbackQuery,
) -> None:
    if not is_admin(callback.from_user.id):
        await deny_access(callback)
        return

    text = (
        "⚙️ <b>Настройки</b>\n\n"
        "🔹 Система администратора работает.\n"
        "🔹 Защита по Telegram ID включена.\n"
        "🔹 Логирование включено.\n"
        "🔹 История рассылок включена.\n"
        "🔹 База данных: SQLite."
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=admin_keyboard(),
        )
    except TelegramBadRequest as error:
        if "message is not modified" not in str(error):
            raise

    logger.info(
        "Admin %s | action=admin_settings",
        callback.from_user.id,
    )

    await callback.answer()


# =========================================================
# BACK TO ADMIN PANEL
# =========================================================

@router.callback_query(F.data == "admin_back")
async def admin_back(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if not is_admin(callback.from_user.id):
        await deny_access(callback)
        return

    await state.clear()

    text = (
        "👨‍💻 <b>Панель администратора</b>\n\n"
        "Выберите нужный раздел:"
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=admin_keyboard(),
        )
    except TelegramBadRequest as error:
        if "message is not modified" not in str(error):
            raise

    await callback.answer()


# =========================================================
# STATISTICS — REPLY BUTTON
# =========================================================

@router.message(F.text == "📊 Статистика")
async def statistics_button(
    message: Message,
) -> None:
    if not is_admin(message.from_user.id):
        return

    count = db.count_students()

    logger.info(
        "Admin %s | action=statistics_button | students=%s",
        message.from_user.id,
        count,
    )

    await message.answer(
        "📊 <b>Статистика</b>\n\n"
        f"👥 Зарегистрированных студентов: "
        f"<b>{count}</b>",
    )


# =========================================================
# USERS — REPLY BUTTON
# =========================================================

@router.message(F.text == "👥 Пользователи")
async def users_button(
    message: Message,
) -> None:
    if not is_admin(message.from_user.id):
        return

    students = db.get_all_students()

    if not students:
        await message.answer(
            "👥 <b>Пользователи</b>\n\n"
            "📭 В базе пока нет "
            "зарегистрированных студентов."
        )
        return

    text = (
        "👥 <b>Пользователи</b>\n\n"
        f"Всего зарегистрировано: "
        f"<b>{len(students)}</b>\n\n"
    )

    for student in students[:20]:
        text += (
            f"🆔 <code>{student['telegram_id']}</code>\n"
            f"👤 {student['first_name']} "
            f"{student['last_name']}\n"
            f"🎂 {student['age']}\n"
            f"📱 {student['phone']}\n"
            "━━━━━━━━━━━━━━\n"
        )

    if len(students) > 20:
        text += (
            f"\nПоказаны первые 20 "
            f"из {len(students)} пользователей."
        )

    await message.answer(text)


# =========================================================
# HISTORY — REPLY BUTTON
# =========================================================

@router.message(F.text == "📨 История")
async def history_button(
    message: Message,
) -> None:
    if not is_admin(message.from_user.id):
        return

    advertisements = db.get_advertisement_history(
        limit=20,
    )

    if not advertisements:
        await message.answer(
            "📨 <b>История рассылок</b>\n\n"
            "📭 Рассылок пока не было."
        )
        return

    text = (
        "📨 <b>История рассылок</b>\n\n"
        f"Всего показано: "
        f"<b>{len(advertisements)}</b>\n\n"
    )

    for advertisement in advertisements:
        message_text = advertisement["message_text"]

        if not message_text:
            message_text = "Медиа-сообщение"

        if len(message_text) > 80:
            message_text = (
                message_text[:80]
                + "..."
            )

        text += (
            f"🆔 <b>#{advertisement['id']}</b>\n"
            f"📅 {advertisement['created_at']}\n"
            f"📝 {message_text}\n"
            f"👥 Получателей: "
            f"<b>{advertisement['total_users']}</b>\n"
            f"✅ Успешно: "
            f"<b>{advertisement['successful_sends']}</b>\n"
            f"❌ Ошибок: "
            f"<b>{advertisement['failed_sends']}</b>\n"
            "━━━━━━━━━━━━━━\n"
        )

    await message.answer(text)


# =========================================================
# SETTINGS — REPLY BUTTON
# =========================================================

@router.message(F.text == "⚙️ Настройки")
async def settings_button(
    message: Message,
) -> None:
    if not is_admin(message.from_user.id):
        return

    await message.answer(
        "⚙️ <b>Настройки</b>\n\n"
        "🔹 Система администратора работает.\n"
        "🔹 Защита по Telegram ID включена.\n"
        "🔹 Логирование включено.\n"
        "🔹 История рассылок включена.\n"
        "🔹 База данных: SQLite."
    )