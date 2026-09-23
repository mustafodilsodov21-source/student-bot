import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from data.config import ADMIN_IDS
from keyboards.default.main import get_main_keyboard
from loader import db
from states.main import EditState, RegisterState


router = Router()

logger = logging.getLogger(__name__)


# ============================================================
# HELPERS
# ============================================================

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def get_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    return get_main_keyboard(
        is_admin=is_admin(user_id)
    )


def back_keyboard() -> ReplyKeyboardMarkup:
    """
    Keyboard used during registration.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="↩️ Назад"
                ),
            ],
        ],
        resize_keyboard=True,
    )


def phone_keyboard() -> ReplyKeyboardMarkup:
    """
    Keyboard for entering phone number.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📱 Отправить номер",
                    request_contact=True,
                ),
            ],
            [
                KeyboardButton(
                    text="↩️ Назад"
                ),
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def delete_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да, удалить",
                    callback_data="delete_confirm",
                ),
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="delete_cancel",
                ),
            ],
        ]
    )


# ============================================================
# /START
# ============================================================

@router.message(CommandStart())
async def start(
    message: Message,
    state: FSMContext,
) -> None:
    await state.clear()

    user_id = message.from_user.id

    logger.info(
        "User %s | command=/start | name=%s",
        user_id,
        message.from_user.first_name,
    )

    await message.answer(
        f"Здравствуйте, <b>{message.from_user.first_name}</b>!\n\n"
        "🎓 <b>Student Bot</b>\n"
        "С помощью этого бота можно зарегистрировать "
        "и управлять данными студента.",
        reply_markup=get_keyboard(user_id),
    )


# ============================================================
# /CANCEL
# ============================================================

@router.message(Command("cancel"))
async def cancel(
    message: Message,
    state: FSMContext,
) -> None:
    await state.clear()

    user_id = message.from_user.id

    logger.info(
        "User %s | action=cancel",
        user_id,
    )

    await message.answer(
        "❌ Действие отменено.",
        reply_markup=get_keyboard(user_id),
    )


# ============================================================
# REGISTRATION START
# ============================================================

@router.message(F.text == "📝 Регистрация")
async def registration_start(
    message: Message,
    state: FSMContext,
) -> None:
    user_id = message.from_user.id

    if db.get_student(user_id):
        await message.answer(
            "⚠️ Вы уже зарегистрированы.\n\n"
            "Если хотите изменить данные, "
            "используйте кнопку «✏️ Изменить данные».",
        )
        return

    await state.clear()

    await state.set_state(
        RegisterState.first_name
    )

    logger.info(
        "User %s | action=registration_started",
        user_id,
    )

    await message.answer(
        "📝 <b>Регистрация</b>\n\n"
        "Введите ваше имя:",
        reply_markup=back_keyboard(),
    )


# ============================================================
# REGISTRATION — FIRST NAME
# ============================================================

@router.message(RegisterState.first_name)
async def registration_first_name(
    message: Message,
    state: FSMContext,
) -> None:

    # BACK
    if message.text == "↩️ Назад":
        await state.clear()

        await message.answer(
            "↩️ Регистрация отменена.",
            reply_markup=get_keyboard(
                message.from_user.id
            ),
        )
        return

    if not message.text:
        await message.answer(
            "Введите имя текстом.",
            reply_markup=back_keyboard(),
        )
        return

    first_name = message.text.strip()

    if len(first_name) < 2:
        await message.answer(
            "Имя слишком короткое. "
            "Введите настоящее имя.",
            reply_markup=back_keyboard(),
        )
        return

    await state.update_data(
        first_name=first_name,
    )

    await state.set_state(
        RegisterState.last_name
    )

    await message.answer(
        "Введите вашу фамилию:",
        reply_markup=back_keyboard(),
    )


# ============================================================
# REGISTRATION — LAST NAME
# ============================================================

@router.message(RegisterState.last_name)
async def registration_last_name(
    message: Message,
    state: FSMContext,
) -> None:

    # BACK
    if message.text == "↩️ Назад":
        await state.set_state(
            RegisterState.first_name
        )

        await message.answer(
            "↩️ Хорошо.\n\n"
            "Введите ваше имя:",
            reply_markup=back_keyboard(),
        )
        return

    if not message.text:
        await message.answer(
            "Введите фамилию текстом.",
            reply_markup=back_keyboard(),
        )
        return

    last_name = message.text.strip()

    if len(last_name) < 2:
        await message.answer(
            "Фамилия слишком короткая.",
            reply_markup=back_keyboard(),
        )
        return

    await state.update_data(
        last_name=last_name,
    )

    await state.set_state(
        RegisterState.age
    )

    await message.answer(
        "Введите ваш возраст числом.\n\n"
        "Например: <b>13</b>",
        reply_markup=back_keyboard(),
    )


# ============================================================
# REGISTRATION — AGE
# ============================================================

@router.message(RegisterState.age)
async def registration_age(
    message: Message,
    state: FSMContext,
) -> None:

    # BACK
    if message.text == "↩️ Назад":
        await state.set_state(
            RegisterState.last_name
        )

        await message.answer(
            "↩️ Хорошо.\n\n"
            "Введите вашу фамилию:",
            reply_markup=back_keyboard(),
        )
        return

    if not message.text or not message.text.isdigit():
        await message.answer(
            "⚠️ Возраст должен быть числом.\n"
            "Например: 13",
            reply_markup=back_keyboard(),
        )
        return

    age = int(message.text)

    if age < 1 or age > 100:
        await message.answer(
            "⚠️ Введите корректный возраст.",
            reply_markup=back_keyboard(),
        )
        return

    await state.update_data(
        age=age,
    )

    await state.set_state(
        RegisterState.phone
    )

    await message.answer(
        "Введите номер телефона или "
        "нажмите кнопку ниже:",
        reply_markup=phone_keyboard(),
    )


# ============================================================
# REGISTRATION — PHONE
# ============================================================

@router.message(RegisterState.phone)
async def registration_phone(
    message: Message,
    state: FSMContext,
) -> None:

    # BACK
    if message.text == "↩️ Назад":
        await state.set_state(
            RegisterState.age
        )

        await message.answer(
            "↩️ Хорошо.\n\n"
            "Введите ваш возраст числом.\n\n"
            "Например: <b>13</b>",
            reply_markup=back_keyboard(),
        )
        return

    if message.contact:
        phone = message.contact.phone_number

    elif message.text:
        phone = message.text.strip()

    else:
        await message.answer(
            "⚠️ Отправьте номер телефона.",
            reply_markup=phone_keyboard(),
        )
        return

    phone = phone.strip()

    if len(phone) < 7:
        await message.answer(
            "⚠️ Номер телефона выглядит неправильно.",
            reply_markup=phone_keyboard(),
        )
        return

    data = await state.get_data()

    try:
        db.add_student(
            telegram_id=message.from_user.id,
            first_name=data["first_name"],
            last_name=data["last_name"],
            age=data["age"],
            phone=phone,
        )

    except Exception:
        logger.exception(
            "User %s | registration database error",
            message.from_user.id,
        )

        await message.answer(
            "❌ Не удалось сохранить данные. "
            "Попробуйте ещё раз.",
            reply_markup=phone_keyboard(),
        )
        return

    await state.clear()

    logger.info(
        "User %s | action=registration_completed | "
        "name=%s %s",
        message.from_user.id,
        data["first_name"],
        data["last_name"],
    )

    await message.answer(
        "✅ <b>Регистрация успешно завершена!</b>\n\n"
        f"👤 Имя: {data['first_name']}\n"
        f"📝 Фамилия: {data['last_name']}\n"
        f"🎂 Возраст: {data['age']}\n"
        f"📱 Телефон: {phone}",
        reply_markup=get_keyboard(
            message.from_user.id,
        ),
    )


# ============================================================
# MY DATA
# ============================================================

@router.message(F.text == "👤 Мои данные")
async def my_data(
    message: Message,
) -> None:
    user_id = message.from_user.id

    student = db.get_student(user_id)

    if not student:
        await message.answer(
            "ℹ️ Вы ещё не зарегистрированы.",
        )
        return

    logger.info(
        "User %s | action=view_profile",
        user_id,
    )

    await message.answer(
        "👤 <b>Ваши данные</b>\n\n"
        f"🆔 ID: {student['id']}\n"
        f"👤 Имя: {student['first_name']}\n"
        f"📝 Фамилия: {student['last_name']}\n"
        f"🎂 Возраст: {student['age']}\n"
        f"📱 Телефон: {student['phone']}\n"
        f"📅 Регистрация: {student['created_at']}",
    )


# ============================================================
# EDIT DATA
# ============================================================

@router.message(F.text == "✏️ Изменить данные")
async def edit_start(
    message: Message,
    state: FSMContext,
) -> None:
    user_id = message.from_user.id

    student = db.get_student(user_id)

    if not student:
        await message.answer(
            "ℹ️ Вы ещё не зарегистрированы.",
        )
        return

    await state.set_state(
        EditState.field,
    )

    logger.info(
        "User %s | action=edit_started",
        user_id,
    )

    await message.answer(
        "✏️ <b>Что хотите изменить?</b>\n\n"
        "1️⃣ Имя\n"
        "2️⃣ Фамилию\n"
        "3️⃣ Возраст\n"
        "4️⃣ Телефон\n\n"
        "Введите номер от 1 до 4.",
    )


@router.message(EditState.field)
async def edit_field(
    message: Message,
    state: FSMContext,
) -> None:
    fields = {
        "1": "first_name",
        "2": "last_name",
        "3": "age",
        "4": "phone",
    }

    if message.text not in fields:
        await message.answer(
            "⚠️ Введите число от 1 до 4.",
        )
        return

    await state.update_data(
        field=fields[message.text],
    )

    await state.set_state(
        EditState.value,
    )

    await message.answer(
        "Введите новое значение:",
    )


@router.message(EditState.value)
async def edit_value(
    message: Message,
    state: FSMContext,
) -> None:
    if not message.text:
        await message.answer(
            "Введите новое значение.",
        )
        return

    data = await state.get_data()
    field = data["field"]

    student = db.get_student(
        message.from_user.id,
    )

    if not student:
        await state.clear()

        await message.answer(
            "❌ Ваши данные не найдены.",
        )
        return

    first_name = student["first_name"]
    last_name = student["last_name"]
    age = student["age"]
    phone = student["phone"]

    value = message.text.strip()

    if field == "first_name":
        if len(value) < 2:
            await message.answer(
                "Имя слишком короткое.",
            )
            return

        first_name = value

    elif field == "last_name":
        if len(value) < 2:
            await message.answer(
                "Фамилия слишком короткая.",
            )
            return

        last_name = value

    elif field == "age":
        if not value.isdigit():
            await message.answer(
                "Возраст должен быть числом.",
            )
            return

        age = int(value)

        if age < 1 or age > 100:
            await message.answer(
                "Введите корректный возраст.",
            )
            return

    elif field == "phone":
        if len(value) < 7:
            await message.answer(
                "Номер телефона выглядит неправильно.",
            )
            return

        phone = value

    try:
        updated = db.update_student(
            telegram_id=message.from_user.id,
            first_name=first_name,
            last_name=last_name,
            age=age,
            phone=phone,
        )

    except Exception:
        logger.exception(
            "User %s | profile update database error",
            message.from_user.id,
        )

        await message.answer(
            "❌ Не удалось изменить данные. "
            "Попробуйте ещё раз.",
        )
        return

    if not updated:
        await state.clear()

        await message.answer(
            "❌ Не удалось найти вашу запись.",
        )
        return

    await state.clear()

    logger.info(
        "User %s | action=profile_updated | field=%s",
        message.from_user.id,
        field,
    )

    await message.answer(
        "✅ <b>Данные успешно изменены!</b>",
        reply_markup=get_keyboard(
            message.from_user.id,
        ),
    )


# ============================================================
# DELETE DATA
# ============================================================

@router.message(F.text == "🗑 Удалить данные")
async def delete_student(
    message: Message,
) -> None:
    user_id = message.from_user.id

    student = db.get_student(user_id)

    if not student:
        await message.answer(
            "ℹ️ Ваших данных нет в базе.",
        )
        return

    await message.answer(
        "⚠️ <b>Удалить ваши данные?</b>\n\n"
        "Это действие нельзя отменить.",
        reply_markup=delete_confirm_keyboard(),
    )


@router.callback_query(F.data == "delete_confirm")
async def delete_confirm(
    callback: CallbackQuery,
) -> None:
    user_id = callback.from_user.id

    deleted = db.delete_student(user_id)

    if not deleted:
        await callback.answer(
            "Данные уже удалены.",
            show_alert=True,
        )
        return

    logger.info(
        "User %s | action=profile_deleted",
        user_id,
    )

    await callback.message.edit_text(
        "🗑 <b>Ваши данные удалены.</b>",
    )

    await callback.message.answer(
        "Главное меню:",
        reply_markup=get_keyboard(user_id),
    )

    await callback.answer(
        "Данные удалены.",
    )


@router.callback_query(F.data == "delete_cancel")
async def delete_cancel(
    callback: CallbackQuery,
) -> None:
    await callback.message.edit_text(
        "❌ Удаление отменено.",
    )

    await callback.answer()


# ============================================================
# ADMIN: ALL STUDENTS
# ============================================================

@router.message(F.text == "👥 Все студенты")
async def all_students(
    message: Message,
) -> None:
    user_id = message.from_user.id

    if not is_admin(user_id):
        logger.warning(
            "User %s | unauthorized action=all_students",
            user_id,
        )

        await message.answer(
            "❌ У вас нет доступа к этому разделу.",
        )
        return

    students = db.get_all_students()

    logger.info(
        "Admin %s | action=view_all_students | count=%s",
        user_id,
        len(students),
    )

    if not students:
        await message.answer(
            "📭 В базе пока нет студентов.",
        )
        return

    text = "👥 <b>Все студенты</b>\n\n"

    for student in students:
        text += (
            f"🆔 ID: {student['id']}\n"
            f"👤 {student['first_name']} "
            f"{student['last_name']}\n"
            f"🎂 Возраст: {student['age']}\n"
            f"📱 Телефон: {student['phone']}\n"
            f"📅 {student['created_at']}\n"
            "━━━━━━━━━━━━━━\n"
        )

    await message.answer(text)


# ============================================================
# ADMIN: STATISTICS
# ============================================================

@router.message(Command("stats"))
async def stats(
    message: Message,
) -> None:
    user_id = message.from_user.id

    if not is_admin(user_id):
        logger.warning(
            "User %s | unauthorized command=/stats",
            user_id,
        )

        await message.answer(
            "❌ У вас нет доступа.",
        )
        return

    count = db.count_students()

    logger.info(
        "Admin %s | action=stats | students=%s",
        user_id,
        count,
    )

    await message.answer(
        "📊 <b>Статистика</b>\n\n"
        f"👥 Всего студентов: <b>{count}</b>",
    )


# ============================================================
# ADMIN: DELETE STUDENT
# ============================================================

@router.message(Command("delete"))
async def delete_student_by_admin(
    message: Message,
) -> None:
    user_id = message.from_user.id

    if not is_admin(user_id):
        await message.answer(
            "❌ У вас нет доступа.",
        )
        return

    if not message.text:
        await message.answer(
            "❌ Использование:\n"
            "<code>/delete TELEGRAM_ID</code>",
        )
        return

    parts = message.text.split()

    if len(parts) != 2:
        await message.answer(
            "❌ Использование:\n"
            "<code>/delete TELEGRAM_ID</code>\n\n"
            "Например:\n"
            "<code>/delete 123456789</code>",
        )
        return

    try:
        telegram_id = int(parts[1])
    except ValueError:
        await message.answer(
            "❌ Telegram ID должен быть числом.",
        )
        return

    deleted = db.delete_student_by_telegram_id(
        telegram_id,
    )

    if deleted:
        logger.info(
            "Admin %s | action=delete_student | target=%s",
            user_id,
            telegram_id,
        )

        await message.answer(
            f"✅ Студент с Telegram ID "
            f"<code>{telegram_id}</code> удалён.",
        )
    else:
        await message.answer(
            f"❌ Студент с Telegram ID "
            f"<code>{telegram_id}</code> не найден.",
        )