from data_driver import sql
from collections import defaultdict


def daily_bags_by_serial_numder(serial_key):
    data = sql.get_today_data_by_serial_key(serial_key)

    today_bags = 0
    _bags = data[0].bags

    for d in data:
        if _bags != d.bags:
            today_bags += d.bags - _bags
            _bags = d.bags

    return today_bags

def total_bags(serial_key):
    robot  = sql.get_robot_by_serial_key(serial_key)
    
    if robot.type == "KAWASAKI":
        return sql.get_last_data_by_serial_key(serial_key).bags
    elif robot.type == "STEP":
        data = sql.get_all_reports(serial_key)
        total = 0
        max_bags = 0

        for bag in data:
            if bag == 0:
                total += max_bags
                max_bags = 0
            else:
                max_bags = max(max_bags, bag)

        total += max_bags
        return total
    else:
        return 0

def last_data(serial_key):
    return sql.get_last_data_by_serial_key(serial_key)

def daily_bags_every_profile(serial_key):
    today_data = sql.get_today_data_by_serial_key(serial_key)

    result = defaultdict(int)
    last_bags = {}

    for data in today_data:
        profile = data["name"]
        bags = data["bags"]

        if profile == "ПРОФИЛЬ НЕ ГОТОВ":
            continue

        if profile not in last_bags:
            last_bags[profile] = bags
            continue

        diff = bags - last_bags[profile]

        if diff < 0:
            diff = bags

        result[profile] += diff
        last_bags[profile] = bags

    return dict(result)