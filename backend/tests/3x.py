import json
from datetime import datetime, timedelta
import requests

session = requests.Session()

# Функция для рекурсивного форматирования JSON
def format_json_recursively(data, indent=4):
    """
    Рекурсивно форматирует JSON-строку, включая вложенные строки, которые тоже являются JSON.
    """
    if isinstance(data, str):
        # Пытаемся преобразовать строку в JSON
        try:
            parsed_data = json.loads(data)
            # Если это удалось, рекурсивно форматируем этот JSON
            return format_json_recursively(parsed_data, indent)
        except (json.JSONDecodeError, TypeError):
            # Если не удалось преобразовать, возвращаем строку как есть
            return data
    elif isinstance(data, dict):
        # Если это словарь, форматируем каждое значение
        return {key: format_json_recursively(value, indent) for key, value in data.items()}
    elif isinstance(data, list):
        # Если это список, форматируем каждый элемент
        return [format_json_recursively(item, indent) for item in data]
    else:
        # Если это не строка, не список и не словарь, возвращаем как есть (например, int, float)
        return data

def print_formatted_json(data, indent=4):
    """
    Печатает отформатированный JSON-объект.
    """
    formatted_data = format_json_recursively(data, indent)
    print(json.dumps(formatted_data, indent=indent, ensure_ascii=False))


# Авторизация
url = "https://185.233.81.223:55555/login"
payload = {
    'username': 'tgbot',
    'password': 'tgbot'
}
headers = {}

response = session.post(url, headers=headers, data=payload, verify=False)
login_response = response.json()
print("login:")
print_formatted_json(login_response)  # Используем функцию для форматированного вывода

# Получение трафика клиента
url = "https://185.233.81.223:55555/panel/api/inbounds/getClientTraffics/pzr3gteh"
payload = {}
headers = {
    'Accept': 'application/json'
}

response = session.get(url, headers=headers, data=payload, verify=False)
traffic_response = response.json()
print("traffic:")
print_formatted_json(traffic_response)  # Используем функцию для форматированного вывода

# Добавление нового клиента
url = "https://185.233.81.223:55555/panel/api/inbounds/addClient"

# Создаем настройки в виде строки JSON
settings = {
    "clients": [
        {
            "id": "95e4e7bb-7796-47e7-e8a7-546454543",
            "alterId": 0,
            "email": "testing",
            "limitIp": 2,
            "totalGB": 1 * 1024 ** 3,  # 1 GB в байтах
            "expiryTime": int((datetime.now() + timedelta(hours=1)).timestamp() * 1000),
            # Время через час в миллисекундах
            "enable": True,
            "tgId": "",
            "subId": ""
        }
    ]
}

payload = {
    "id": 3,
    "settings": json.dumps(settings)  # Преобразуем настройки в строку JSON
}

headers = {
    'Accept': 'application/json'
}

response = session.post(url, headers=headers, data=payload, verify=False)
add_client_response = response.json()
print("add new client:")
print_formatted_json(add_client_response)  # Используем функцию для форматированного вывода

# Получение IP клиента
url = "https://185.233.81.223:55555/panel/api/inbounds/clientIps/testing"
payload = {}
headers = {
    'Accept': 'application/json'
}

response = session.post(url, headers=headers, data=payload, verify=False)
client_ips_response = response.json()
print("client IPs:")
print_formatted_json(client_ips_response)  # Используем функцию для форматированного вывода

# Получение информации об inbound
url = "https://185.233.81.223:55555/panel/api/inbounds/get/3"
payload = {}
headers = {
    'Accept': 'application/json'
}

response = session.get(url, headers=headers, data=payload, verify=False)
inbound_response = response.json()
print("inbound:")
print_formatted_json(inbound_response)  # Используем функцию для форматированного вывода
