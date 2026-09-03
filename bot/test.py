import requests
from data_driver import config


url = config().get("SERVER_URL")
URL = f"http://{url}/get_robot_data/1"
print(URL)
r = requests.get(
    f'{URL}'            
)

print(r)