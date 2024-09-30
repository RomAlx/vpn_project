import requests

data = {
    "price_amount": 100.0,
    "price_currency": "USD",
    "pay_currency": "TON",
    "order_id": "your_order_id_123",
}

headers = {
            "x-api-key": "DB23V4V-X90MKXT-P4APCHS-C4NSB72",
            "Content-Type": "application/json"
        }

response = requests.post(f"https://api.nowpayments.io/v1/payment", json=data, headers=headers)

if response.status_code != 200:
    print(f"Ошибка при запросе: {response.status_code} - {response.text}")
else:
    print(response)