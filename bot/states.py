from aiogram.fsm.state import State, StatesGroup



class States(StatesGroup):
    authorization = State()
    waiting_data = State()

    admin = State()