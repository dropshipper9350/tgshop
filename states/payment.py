from aiogram.fsm.state import State, StatesGroup


class PaymentState(StatesGroup):
    waiting_for_screenshot = State()
    waiting_for_custom_quantity = State()