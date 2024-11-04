import os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo


class Chat:
    def __init__(self):
        load_dotenv()
        self.base_dir = os.getenv('BASE_DIR')
        self.start_message = (f'**LikeVPN** - это сервис доступа к любимым социальным сетям и сервисам с безопасной '
                              f'передачей данных в зашифрованном виде.\n'
                              f'Настройка в 2 клика.\n'
                              f'🚀 Скорость от 100 Мбит/с.\n'
                              f'🖥 Собственные сервера: 🇩🇪 🇫🇮 ')
        self.start_image = '/chat/img/start_img.jpg'
        self.video_instruction = '/chat/video/instruction.mp4'
        self.default = 'I do not understand'

    def start_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = [
            [
                InlineKeyboardButton(text="Создать ключ ⚡️", callback_data='user_create_key'),
                InlineKeyboardButton(text="Мои ключи 🔑", callback_data='user_keys')
            ],
            [
                InlineKeyboardButton(text="Баланс 💎", callback_data='user_balance'),
                InlineKeyboardButton(text="Оплата 🛍", callback_data='user_top_up')
            ],
            [
                InlineKeyboardButton(text="Инструкция 🧾", callback_data='instruction')
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    def top_up_currency_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = [
            [
                InlineKeyboardButton(text="USDT (Tether)", callback_data='top_up_USDT'),
                InlineKeyboardButton(text="TON (Toncoin)", callback_data='top_up_TON'),
            ],
            [
                InlineKeyboardButton(text="XMR (Monero)", callback_data='top_up_XMR'),
                InlineKeyboardButton(text="LTC (Litecoin)", callback_data='top_up_LTC'),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)

    def amount_keyboard(self, currency: str) -> InlineKeyboardMarkup:
        keyboard = [
            [
                InlineKeyboardButton(text="10 💲", callback_data=f'top_up_{currency}_10'),
                InlineKeyboardButton(text="25 💲", callback_data=f'top_up_{currency}_25'),
                InlineKeyboardButton(text="100 💲", callback_data=f'top_up_{currency}_100'),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)

    def subscription_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton(text="День | 0.5$", callback_data='subscribe_day')],
            [InlineKeyboardButton(text="Месяц | 4.8$", callback_data='subscribe_month')],
            [InlineKeyboardButton(text="3 месяца | 13.5$", callback_data='subscribe_3_months')],
            [InlineKeyboardButton(text="Год | 129.6$", callback_data='subscribe_year')]
        ]
        return InlineKeyboardMarkup(keyboard)

    def apps_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = [
            [
                InlineKeyboardButton(text="Скачать для IPhone", url="https://apps.apple.com/app/id6450534064")
            ],
            [
                InlineKeyboardButton(text="Скачать для Android", url="https://play.google.com/store/apps/details?id=com.v2raytun.android"),
            ],
            [
                InlineKeyboardButton(text="Инструкция 🧾", callback_data='instruction')
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
