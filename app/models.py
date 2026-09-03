from pydantic import BaseModel
from dataclasses import dataclass
from datetime import datetime


class ReportData(BaseModel):
    name                : str
    total_bags          : int
    profile_loaded      : str
    errors              : list
    robot_type          : str
    left_status         : str
    right_status        : str


@dataclass
class Report:
    index               : int
    time                : datetime
    bags                : int
    profile_loaded      : str
    errors              : str
    left_status         : str
    right_status        : str


@dataclass
class Robot:
    id                  : int
    name                : str
    type               : str    



class DTO:
    @classmethod
    def sql_to_Report(cls, data):
        return Report(
            index = data[0],
            time=datetime.strptime(data[1], "%Y-%m-%d %H:%M:%S"),
            bags=data[2],
            profile_loaded=data[3],
            errors=data[4],
            left_status=data[5],
            right_status=data[6]
        )

    @classmethod
    def sql_to_Robot(cls, data):
        return Robot(
            id=data[1],
            name=data[2],
            type=data[3]
        )
        