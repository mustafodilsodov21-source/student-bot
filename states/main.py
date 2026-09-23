
from aiogram.fsm.state import State, StatesGroup


class RegisterState(StatesGroup):
    """
    Student registration flow.
    """

    first_name = State()
    last_name = State()
    age = State()
    phone = State()


class EditState(StatesGroup):
    """
    Student profile editing flow.
    """

    field = State()
    value = State()


class AdminStates(StatesGroup):
    """
    Administrator workflows.
    """

    waiting_for_ad = State()
    confirming_ad = State()

