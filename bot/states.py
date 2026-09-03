from aiogram.fsm.state import State, StatesGroup
from data_driver import sql, DataDriver


class Session:
    def __init__(self, user_id, driver: DataDriver=sql):
        self.driver = driver
        self.user_id = user_id

    @property
    def robot(self):
        robot_id = self.driver.get_robot_by_user_id(self.user_id)
        

class States(StatesGroup):
    authorization = State()
    waiting_data = State()

    admin = State()