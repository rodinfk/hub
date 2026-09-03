import requests

from time import sleep as wait
from dotenv import dotenv_values


def config():
    return dotenv_values("config.env")


DATA_SERVER_URL = config().get("DATA_SERVER_URL")
SERIAL_KEY = config().get("SERIAL_KEY")
PROJECT_NAME = config().get("PROJECT_NAME")
ROBOT_TYPE = config().get("ROBOT_TYPE")

url = f"http://{DATA_SERVER_URL}/set_robot_data/{SERIAL_KEY}"

headers = {
    "Content-Type": "application/json"
    }

while True:
    data = dict()

    try:
        r = requests.get("http://127.0.0.1/api/system/data")
        data = r.json()
        print(f"Данные получены - {data}")
    except requests.exceptions.ConnectionError:
        print('Не запущена андромеда, данные не дернулись')
    except requests.exceptions.JSONDecodeError:
        print('У андромеды нет связи с роботом, данные не дернулись')
        


    if data:
        data["name"] = PROJECT_NAME
        data["type"] = ROBOT_TYPE
        try:
            r = requests.post(url, json=data)
            print(f'Status - {r.status_code}')
        except requests.exceptions.ConnectionError:
            print('Ошибка при отправке отчета, не удалось получить соединение с сервером. Проверьте интернет')
        except requests.exceptions.JSONDecodeError:
            print('Ошибка от сервера')

    wait(5)