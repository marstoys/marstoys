from aiogram.fsm.state import StatesGroup, State



class OrderState(StatesGroup):
    waiting_for_order_number = State()