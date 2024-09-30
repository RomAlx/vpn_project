import hashlib
import json
import os
import uuid
from datetime import datetime, time
import requests

from backend.logs.logger import Logger
from backend.models import User
from backend.repositories.vpn_keys_repository import VPNKeysRepository
from backend.repositories.user_repository import UserRepository


class VPNKeyManager:
    def __init__(self):
        self.logger = Logger(name="manager.vpn").get_logger()
        self.base_url = os.getenv('VPN_BASE_URL')
        self.username = os.getenv('VPN_USERNAME')
        self.password = os.getenv('VPN_PASSWORD')
        self.server_address = os.getenv('VPN_SERVER_ADDRESS')
        self.server_port = os.getenv("VPN_SERVER_PORT")
        self.pbk = os.getenv("VPN_PUBLIC_KEY")
        self.vpn_keys_repo = VPNKeysRepository()
        self.user_repo = UserRepository()

    def _login(self) -> bool:
        """Аутентификация в панели"""
        url = f"{self.base_url}/login"
        payload = {
            'username': self.username,
            'password': self.password
        }

        self.session = requests.Session()
        response = self.session.post(url, headers={}, data=payload, verify=False)

        if response.status_code == 200 and response.json().get("success"):
            print("Успешная аутентификация")
            return True
        else:
            print(f"Ошибка аутентификации: {response.status_code} - {response.text}")
            return False

    def get_vpn_keys(self, user_id: int) -> str:
        """Получение всех ключей по user_id и удаление просроченных"""
        if not self._login():
            return "Аутентификация не удалась. Дальнейшие действия невозможны."

        user_keys = self.vpn_keys_repo.get_vpn_keys_by_user_id(user_id)
        result = []

        for key in user_keys:
            if key.expires_at < datetime.now():
                self.vpn_keys_repo.delete_vpn_key(key.id)
                continue

            formatted_expiry = key.expires_at.strftime('%Y-%m-%d %H:%M:%S')
            result.append(f"Key: {key.key}, Expires at: {formatted_expiry}")

        return "\n".join(result)

    def create_vpn_client(self, user: User, expiration_time: int, gb_limit: int) -> str:
        self.logger.info(f"Начало создания VPN клиента для user_id: {user.id}")
        if not self._login():
            print("Аутентификация не удалась. Дальнейшие действия невозможны.")
            self.logger.error("Аутентификация не удалась. Дальнейшие действия невозможны.")
            return "Аутентификация не удалась. Дальнейшие действия невозможны."

        self.logger.info(f"User: {user}")

        client_id = f'{user.id}_' + str(datetime.now().timestamp()).replace('.', '')
        hashed = hashlib.sha1(client_id.encode('utf-8')).hexdigest()
        custom_uuid = str(uuid.UUID(hashed[:32]))



        self.logger.info(f"Сгенерирован UUID: {custom_uuid}")

        try:
            settings = json.dumps({
                "clients": [
                    {
                        "id": custom_uuid,
                        "alterId": 0,
                        "email": client_id,
                        "flow": '',  # Для vless flow должен быть пустым
                        "limitIp": 2,
                        "totalGB": gb_limit * 1024 ** 3,
                        "expiryTime": expiration_time,
                        "enable": True,
                        "tgId": "",
                        "subId": ""
                    }
                ]
            })
            self.logger.info(f"Сформированы настройки клиента: {settings}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Ошибка формирования JSON: {e}")
            return "Ошибка формирования данных."

        payload = {
            "id": 3,
            "settings": settings
        }

        url = f"{self.base_url}/panel/api/inbounds/addClient"
        self.logger.info(f"Отправка запроса на URL: {url}")
        response = self.session.post(url, headers={'Accept': 'application/json'}, json=payload, verify=False)
        self.logger.info(f"Получен ответ: Статус {response.status_code}, Тело: {response.text}")

        if response.status_code == 200 and response.json().get("success"):
            self.vpn_keys_repo.create_vpn_key(user.id, custom_uuid, client_id, expiration_time, gb_limit)
            vless_link = self.generate_vless_link(custom_uuid, client_id)
            self.logger.info(f"Клиент успешно создан. UUID: {custom_uuid}, VLESS ссылка: {vless_link}")
            return vless_link
        else:
            self.logger.error(f"Ошибка создания клиента: {response.status_code} - {response.text}")
            return f"Ошибка создания клиента: {response.status_code} - {response.text}"

    def generate_vless_link(self, uuid, client_id):
        type = "tcp"
        security = "reality"
        fp = "chrome"
        sni = "ya.ru"
        sid='97df02b74a19ae3e'
        vless_link = f"vless://3a97c533-a642-cc31-e3d9-e0ff71f41d4e@185.233.81.223:443/?type=tcp&security=reality&pbk=ROx047mgBklnXeljIIG79NfpyCykSe-r_55PyvkgzVE&fp=chrome&sni=ya.ru&sid=97df02b74a19ae3e&spx=%2F#tgbot-5_1726065358734559"
        vless_link = f"vless://{uuid}@{self.server_address}:{self.server_port}/?type={type}&security={security}&pbk={self.pbk}&fp={fp}&sni={sni}&sid={sid}&spx=%2F#tgbot-{client_id}"
        return vless_link
