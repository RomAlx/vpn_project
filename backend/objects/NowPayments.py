import os
import requests
from dotenv import load_dotenv

load_dotenv()


class NowPayments:
    BASE_URL = "https://api.nowpayments.io/v1"

    def __init__(self):
        self.api_key = os.getenv("NOWPAYMENTS_API_KEY")
        self.project_url = os.getenv("PROJECT_URL")
        self.bot_url = "https://t.me/test_1337_1488_bot"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def create_invoice(self, amount: float, currency: str, order_id: str, pay_currency: str = "TON"):
        # price_amount = 100.0  # Сумма, которую нужно получить
        # price_currency = "USDT"  # Валюта платежа (USDT)
        # pay_currency = "TON"  # Валюта, в которой пользователь будет платить (TON)
        # order_id = "your_order_id_123"  # Уникальный идентификатор заказа
        # success_url = "https://yourdomain.com/payment/success"  # URL для успешного платежа
        # cancel_url = "https://yourdomain.com/payment/cancel"  # URL для отмены платежа
        data = {
            "price_amount": amount,
            "price_currency": currency,
            "pay_currency": pay_currency,
            "order_id": order_id,
            "ipn_callback_url": f"{self.project_url}/api/payment/callback",
            "success_url": f"{self.bot_url}",
            "cancel_url": f"{self.bot_url}"
        }

        response = requests.post(f"{self.BASE_URL}/invoice", json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_payment_status(self, payment_id: str):
        response = requests.get(f"{self.BASE_URL}/payment/{payment_id}", headers=self.headers)
        response.raise_for_status()
        return response.json()
