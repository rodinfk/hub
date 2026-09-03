from fastapi import FastAPI

from contextlib import asynccontextmanager

from data_driver import sql

from models import ReportData

from reports import total_bags
from reports import daily_bags_by_serial_numder
from reports import last_data
from reports import daily_bags_every_profile


@asynccontextmanager
async def lifespan(app: FastAPI):
    sql.create_tables()
    yield
    print("Сервер остановлен")

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def base():
    return {"Hello": "World"}


@app.post("/set_robot_data/{robot_id}")
async def read(robot_id: str, data: ReportData):
    print(data)
    sql.write_report(robot_id, data)

    return {
        "id": robot_id
        }


@app.get("/get_robot/{robot_id}")
async def get_robot(robot_id: str):
    robot = sql.get_robot_by_serial_key(robot_id)
    return {
        "robot": robot.type,
        "name": robot.name
        }


@app.get("/get_total_bags/{robot_id}")
async def get_total_bags(robot_id):
    bags = total_bags(robot_id)

    return {
        "count": bags
        }


@app.get("/get_today_bags/{robot_id}")
async def get_today_bags(robot_id):
    bags = daily_bags_by_serial_numder(robot_id)
    
    return {
        "count": bags
        }


@app.get("/get_last_data/{robot_id}")
async def get_last_data(robot_id):
    data = last_data(robot_id)
    
    return data


@app.get("/get_today_profiles_data/{robot_id}")
async def get_today_profiles_data(robot_id):
    data = daily_bags_every_profile(robot_id)

    return data


import uvicorn

if __name__ == "__main__":
    uvicorn.run("core:app", host="0.0.0.0", port=80, reload=True)