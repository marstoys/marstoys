from aiogram.fsm.state import StatesGroup, State



class RegisterState(StatesGroup):
    first_name = State()
    last_name = State()
    phone_number = State()
    
class MenuState(StatesGroup):
    menu = State()
    subscribe_check = State()

class OrderState(StatesGroup):
    waiting_for_order_number = State()