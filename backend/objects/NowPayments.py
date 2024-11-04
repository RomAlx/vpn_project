import hashlib
import hmac
import json
import os
import time

import requests
from dotenv import load_dotenv
from backend.logs.logger import Logger

load_dotenv()


class NowPayments:
    def __init__(self):
        # Инициализация логгера в начале для записи всех этапов
        self.logger = Logger(name="nowpayments").get_logger()

        # Определение режима работы
        self.is_sandbox = os.getenv("NOWPAYMENTS_SANDBOX", "false").lower() == "true"
        self.logger.info(f"Initializing NowPayments in {'sandbox' if self.is_sandbox else 'production'} mode")

        # Настройка базовых URL и ключей в зависимости от режима
        if self.is_sandbox:
            self.BASE_URL = "https://api-sandbox.nowpayments.io/v1"
            self.api_key = os.getenv("NOWPAYMENTS_API_KEY")
            self.ipn_secret = os.getenv("NOWPAYMENTS_IPN_SECRET")
            self.logger.info("Using sandbox configuration")
        else:
            self.BASE_URL = "https://api.nowpayments.io/v1"
            self.api_key = os.getenv("NOWPAYMENTS_API_KEY")
            self.ipn_secret = os.getenv("NOWPAYMENTS_IPN_SECRET")
            self.logger.info("Using production configuration")

        # Проверка и настройка URL'ов
        self.project_url = os.getenv("PROJECT_URL")
        self.bot_url = os.getenv("TELEGRAM_BOT_URL")

        # Проверка обязательных параметров
        if not self.api_key:
            error_msg = "API key not configured!"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        if not self.ipn_secret:
            self.logger.warning("IPN secret not configured - callback verification will be disabled")

        if not self.project_url:
            error_msg = "PROJECT_URL not configured!"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        if not self.bot_url:
            self.logger.warning("TELEGRAM_BOT_URL not configured, using default")
            self.bot_url = "https://t.me/your_bot"

        # Настройка заголовков
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        # Проверка соединения с API
        try:
            self._check_api_connection()
        except Exception as e:
            self.logger.error(f"Failed to connect to NOWPayments API: {str(e)}")

    def _check_api_connection(self):
        """Проверка соединения с API"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/status",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            self.logger.info("Successfully connected to NOWPayments API")
        except Exception as e:
            self.logger.error(f"API connection check failed: {str(e)}")
            raise

    def verify_nowpayments_signature(self, request_data: bytes, received_signature: str) -> bool:
        """Проверка подписи от NOWPayments"""
        try:
            if not self.ipn_secret:
                self.logger.warning("IPN secret not configured, skipping signature verification")
                return True if self.is_sandbox else False

            calculated_signature = hmac.new(
                self.ipn_secret.encode(),
                request_data,
                hashlib.sha512
            ).hexdigest()

            is_valid = hmac.compare_digest(calculated_signature, received_signature)
            self.logger.info(f"Signature verification {'successful' if is_valid else 'failed'}")
            return is_valid

        except Exception as e:
            self.logger.error(f"Error verifying signature: {str(e)}")
            return True if self.is_sandbox else False

    def create_invoice(self, amount: float, currency: str, order_id: str, pay_currency: str = "TON"):
        """
        Создание инвойса для оплаты

        Args:
            amount (float): Сумма платежа
            currency (str): Валюта суммы (обычно USD)
            order_id (str): Уникальный идентификатор заказа
            pay_currency (str): Валюта, в которой будет производиться оплата
        """
        try:
            self.logger.info(
                f"Creating invoice: amount={amount} {currency}, pay_currency={pay_currency}, order_id={order_id}")

            # Валидация входных данных
            if not isinstance(amount, (int, float)) or amount <= 0:
                raise ValueError(f"Invalid amount: {amount}")
            if not isinstance(order_id, str) or not order_id:
                raise ValueError(f"Invalid order_id: {order_id}")

            # Формирование данных запроса
            data = {
                "price_amount": float(amount),
                "price_currency": currency.upper(),
                "pay_currency": pay_currency.upper(),
                "order_id": order_id,
                "ipn_callback_url": f"{self.project_url}/api/payment/callback",
                "success_url": self.bot_url,
                "cancel_url": self.bot_url,
                "is_fee_paid_by_user": True
            }

            # Логирование запроса
            self.logger.info(f"Request URL: {self.BASE_URL}/invoice")
            self.logger.info(f"Request data: {json.dumps(data)}")

            # Отправка запроса
            response = requests.post(
                f"{self.BASE_URL}/invoice",
                json=data,
                headers=self.headers,
                timeout=30
            )

            # Логирование ответа
            self.logger.info(f"Response status code: {response.status_code}")

            try:
                response_json = response.json()
                self.logger.info(f"Response data: {json.dumps(response_json)}")

                # Проверяем ошибки в ответе
                if not response.ok:
                    error_message = response_json.get('message', 'Unknown error')
                    error_code = response_json.get('code', 'UNKNOWN_ERROR')
                    self.logger.error(f"API Error: {error_code} - {error_message}")
                    raise ValueError(f"API Error: {error_message}")

            except json.JSONDecodeError:
                self.logger.error(f"Failed to decode response: {response.text}")
                raise ValueError("Invalid JSON response from API")

            # Проверка статуса ответа
            response.raise_for_status()

            # Проверка необходимых полей в зависимости от режима
            if self.is_sandbox:
                required_fields = ['id', 'invoice_url', 'token_id']
            else:
                required_fields = ['id', 'invoice_url', 'payment_id']

            missing_fields = [field for field in required_fields if field not in response_json]
            if missing_fields:
                raise ValueError(f"Missing required fields in API response: {missing_fields}")

            # Если это sandbox, используем token_id вместо payment_id
            if self.is_sandbox and 'token_id' in response_json:
                response_json['payment_id'] = response_json['token_id']

            return response_json

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {str(e)}")
            raise
        except ValueError as e:
            self.logger.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            raise

    def get_payment_status(self, payment_id: str):
        """Получение статуса платежа"""
        try:
            if not payment_id:
                raise ValueError("payment_id is required")

            self.logger.info(f"Checking payment status: {payment_id}")

            response = requests.get(
                f"{self.BASE_URL}/payment/{payment_id}",
                headers=self.headers,
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            self.logger.info(f"Payment status response: {json.dumps(result)}")
            return result

        except Exception as e:
            self.logger.error(f"Error getting payment status: {str(e)}")
            raise

    def estimate_price(self, amount: float, currency_from: str, currency_to: str):
        """Получение оценки стоимости в криптовалюте"""
        try:
            if not isinstance(amount, (int, float)) or amount <= 0:
                raise ValueError(f"Invalid amount: {amount}")

            self.logger.info(f"Estimating price: {amount} {currency_from} to {currency_to}")

            response = requests.get(
                f"{self.BASE_URL}/estimate",
                params={
                    "amount": amount,
                    "currency_from": currency_from.upper(),
                    "currency_to": currency_to.upper()
                },
                headers=self.headers,
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            self.logger.info(f"Estimate response: {json.dumps(result)}")
            return result

        except Exception as e:
            self.logger.error(f"Error estimating price: {str(e)}")
            raise

    def get_test_payment_status(self, payment_id: str, status: str = "finished"):
        """Установка тестового статуса платежа (только для sandbox)"""
        if not self.is_sandbox:
            raise ValueError("This method is only available in sandbox mode")

        try:
            if not payment_id:
                raise ValueError("payment_id is required")

            self.logger.info(f"Setting test payment status: {payment_id} -> {status}")

            data = {
                "payment_id": payment_id,
                "payment_status": status
            }

            response = requests.post(
                f"{self.BASE_URL}/payment-status",
                json=data,
                headers=self.headers,
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            self.logger.info(f"Test status response: {json.dumps(result)}")
            return result

        except Exception as e:
            self.logger.error(f"Error setting test payment status: {str(e)}")
            raise

    def simulate_payment(self, payment_id: str, amount: float = None):
        """
        Симуляция процесса оплаты в sandbox режиме

        Args:
            payment_id (str): ID платежа
            amount (float): Сумма платежа (опционально)
        """
        if not self.is_sandbox:
            raise ValueError("This method is only available in sandbox mode")

        try:
            # Симулируем последовательность статусов
            statuses = [
                "waiting",  # Ожидание оплаты
                "confirming",  # Подтверждение транзакции
                "confirmed",  # Транзакция подтверждена
                "sending",  # Отправка средств
                "finished"  # Платёж завершен
            ]

            self.logger.info(f"Starting payment simulation for payment_id: {payment_id}")

            for status in statuses:
                self.logger.info(f"Setting payment status to: {status}")

                data = {
                    "payment_id": payment_id,
                    "payment_status": status,
                }
                if amount and status == "finished":
                    data["price_amount"] = amount

                response = requests.post(
                    f"{self.BASE_URL}/payment-status",
                    json=data,
                    headers=self.headers,
                    timeout=30
                )

                response.raise_for_status()
                result = response.json()
                self.logger.info(f"Status update response: {json.dumps(result)}")

                # Небольшая пауза между статусами
                time.sleep(2)

            self.logger.info("Payment simulation completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error simulating payment: {str(e)}")
            raise