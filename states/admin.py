from aiogram.fsm.state import State, StatesGroup


class AdminState(StatesGroup):
    waiting_for_accounts = State()
    waiting_for_product_name = State()
    waiting_for_product_price = State()
    waiting_for_product_description = State()