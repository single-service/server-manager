import requests
import json
import uuid
import re

PORTAINER_URL = "http://0.0.0.0:9002"
PORTAINER_USERNAME = "admin"
PORTAINER_PASSWORD = "45ROS_!_hen25"

SERVER_HOST = "62.109.31.156"

response = requests.post(
    f"{PORTAINER_URL}/api/auth",
    json={
        "username": PORTAINER_USERNAME,
        "password": PORTAINER_PASSWORD
        }
    )
if response.status_code == 200:
    token = response.json().get("jwt")
    print("token: ", token)
else:
    print("Ошибка авторизации в Portainer: " + response.text)


headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{PORTAINER_URL}/api/endpoints", headers=headers)
# print(f"{PORTAINER_URL}/api/endpoints", response.status_code, response.text)

# environments = response.json()
# for env in environments:
#     with open("environment.json", "w") as json_file:
#         json.dump(env, json_file)
#     print(env)
#     break

headers = {
    "Authorization": f"Bearer {token}",
    # "Content-Type": "multipart-form-data"
}
environment_name = f"c{str(uuid.uuid4()).replace('-', '')}"
# Проверка на соответствие требованиям имени
if not re.match("^[a-zA-Z0-9-_]+$", environment_name):
    raise Exception("Имя окружения содержит недопустимые символы.")
print("environment_name", environment_name)
data = {
    "Name": f"c{str(uuid.uuid4()).replace('-', '')}",
    "EndpointCreationType": 2,
    "URL": f"tcp://{SERVER_HOST}:9001",
    "TLS": True,
    "TLSSkipVerify": True,
    "TLSSkipClientVerify": True,
    "GroupID": 1,
    # Добавьте другие параметры окружения, если необходимо
}
print(data)
response = requests.post(f"{PORTAINER_URL}/api/endpoints", headers=headers, data=data, verify=False)
if response.status_code != 201:
    raise Exception("Ошибка создания окружения в Portainer: " + response.text)