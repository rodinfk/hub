import requests

from aiogram import Bot, Dispatcher
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from states import States

from data_driver import config, sql
from dataclasses import dataclass


TOKEN = "8773506410:AAF-mjJ_GrdLW4YWkPGbFvvrNwCF9YpZUDs"


@dataclass
class BTN_TEXT:
    CONDITION = "Состояние"
    TODAY_PROFILES = "Отчет за сегодня"
    TOTAL_BAGS = "Общее количество мешков"
    TODAY_BAGS = "Мешков за сегодня"



bot = Bot(token=TOKEN)
dp = Dispatcher()

report_btns = [
    [KeyboardButton(text=BTN_TEXT.CONDITION)],
    [KeyboardButton(text=BTN_TEXT.TODAY_PROFILES)],
    [KeyboardButton(text=BTN_TEXT.TODAY_BAGS)],
    [KeyboardButton(text=BTN_TEXT.TOTAL_BAGS)]
]

   


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext):
    user_id = message.chat.id
    await state.set_state(States.authorization)
    await bot.send_message(
        user_id,
        f"""Добро пожаловать в систему отчетов робота-паллетайзера, {message.from_user.full_name}!
Введите серийный номер робота одним сообщением без пробелов и переноса строк:""",
        parse_mode="HTML")


@dp.message(Command("system"))
async def system(message: Message, state: FSMContext):
    user_id = message.chat.id
    
    ADMINS = config().get("ADMINS_ID")

    if user_id == int(ADMINS):
        await bot.send_message(
            user_id,
            "Вы вошли как админ, терминал открыт. break - выход"
            )
        await state.set_state(States.admin)
    else:
        await bot.send_message(
            user_id,
            "Тебя нет в админах."
            )

@dp.message(Command("exit"))
async def exit(message: Message, state: FSMContext):
    user_id = message.chat.id
    sql.delete_user(user_id)
    await bot.send_message(
        user_id,
        f"""Добро пожаловать в систему отчетов робота-паллетайзера, {message.from_user.full_name}!
Введите серийный номер робота одним сообщением без пробелов и переноса строк:""",
        parse_mode="HTML")              
    await state.set_state(States.authorization)
    

@dp.message(Command("help"))
async def help(message: Message):
    user_id = message.chat.id
    await bot.send_message(user_id, 
"/help - список всех команд\n/exit - выход в начало")
    pass



@dp.message(States.authorization)
async def authorization(message: Message, state: FSMContext):
    user_id = message.chat.id
    url = config().get("SERVER_URL")

    try:
        r = requests.get(
            f"{url}/get_robot/{message.text}"
        )

        name = r.json()['name']

        if name is not None:
            keyboard = ReplyKeyboardMarkup(
                keyboard=report_btns,
                resize_keyboard=True,
                input_field_placeholder="Выберите тип отчета"
                )

            await bot.send_message(
                user_id,
                f"Ваш проект - {r.json()['name']}, выберите отчет",
                reply_markup=keyboard
            )

            sql.write_user(user_id, message.text)
            await state.set_state(States.waiting_data)

        else: 
            await bot.send_message(
                user_id,
                f"Ваш проект не найден"
            )


    except requests.exceptions.ConnectionError:
        await bot.send_message(
            user_id,
            "Ошибка при получении данных, не удалось получить соединение с сервером. Попробуйте позже"
            )

@dp.message(States.admin)
async def admin_handler(message: Message, state: FSMContext):
    user_id = message.chat.id
    cmd = message.text

    if cmd == 'break':
        await state.set_state(States.authorization)
        await bot.send_message(
            user_id,
            f"""Добро пожаловать в систему отчетов робота-паллетайзера, {message.from_user.full_name}!
Введите серийный номер робота одним сообщением без пробелов и переноса строк:""",
            parse_mode="HTML")
    elif cmd == '/db':
        db = FSInputFile(sql.db_path)
        await message.answer_document(document=db)  
    else:
        exec(cmd)


@dp.message(States.waiting_data)
async def request_handler(message: Message, state: FSMContext):
    user_id = message.chat.id
    text = message.text

    url = config().get("SERVER_URL")
    robot_id = sql.get_robot_by_user_id(user_id)

    keyboard = ReplyKeyboardMarkup(
        keyboard=report_btns,
        resize_keyboard=True,
        input_field_placeholder="Выберите тип отчета"
    )

    if text == BTN_TEXT.TOTAL_BAGS:
        try:
            r = requests.get(
                f"{url}/get_total_bags/{robot_id}"
            )
        
            await bot.send_message(
                user_id,
                f"Количество мешков - {r.json()['count']}",
                reply_markup=keyboard
            )
    
            sql.write_user(user_id, message.text)
    
        except requests.exceptions.ConnectionError:
            await bot.send_message(
                user_id,
                "Ошибка при получении данных, не удалось получить соединение с сервером. Попробуйте позже"
                )

    elif text == BTN_TEXT.TODAY_PROFILES:
        try:
            r = requests.get(
                f"{url}/get_today_profiles_data/{robot_id}"
            )

            data = r.json()

            answer = ""
            for key, value in data.items():
                answer += f"{key} - {value}\n"
            
            await bot.send_message(
                user_id,
                f"Отчет по профилям (название рецепта - кол-во мешков):\n" + answer,
                reply_markup=keyboard
            )
    
            sql.write_user(user_id, message.text)
    
        except requests.exceptions.ConnectionError:
            await bot.send_message(
                user_id,
                "Ошибка при получении данных, не удалось получить соединение с сервером. Попробуйте позже"
                )
            
    elif text == BTN_TEXT.TODAY_BAGS:
        try:
            r = requests.get(
                f"{url}/get_today_bags/{robot_id}"
            )

            await bot.send_message(
                user_id,
                f"Количество мешков сегодня - {r.json()['count']}",
                reply_markup=keyboard
            )
    
            sql.write_user(user_id, message.text)
    
        except requests.exceptions.ConnectionError:
            await bot.send_message(
                user_id,
                "Ошибка при получении данных, не удалось получить соединение с сервером. Попробуйте позже"
                )

    elif text == BTN_TEXT.CONDITION:
        try:
            r = requests.get(
                f"{url}/get_last_data/{robot_id}"
            )

            data = r.json()
            errors = "НЕТ ОШИБОК" if not data['errors'] else errors

            await bot.send_message(
                user_id,
                f"""Состояние системы:
Профиль - {data['profile_loaded']}
Ошибки - {errors}
Статус левой стороны - {data['left_status']}
Статус правой стороны - {data['right_status']}""",
                reply_markup=keyboard
            )
    
            sql.write_user(user_id, message.text)
    
        except requests.exceptions.ConnectionError:
            await bot.send_message(
                user_id,
                "Ошибка при получении данных, не удалось получить соединение с сервером. Попробуйте позже"
                )

    else:
        await bot.send_message(
            user_id,
            "Не понимаю вас, нажмите кнопку или /help для всех комманд"
            )
                