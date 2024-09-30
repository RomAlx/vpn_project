from datetime import datetime, timedelta
import json
from telegram import Update, ReplyKeyboardRemove
from telegram.constants import ParseMode

from backend.repositories.user_repository import UserRepository as user_repository
from backend.repositories.vpn_keys_repository import VPNKeysRepository as vpn_keys_repository

from ..objects.Telegram import Telegram
from ..objects.NowPayments import NowPayments
from ..objects.VPNKeyManager import VPNKeyManager

from ..logs.logger import Logger
from ..chat.chat_config import Chat


class TelegramController:
    def __init__(self):
        self.logger = Logger(name="controller.telegram").get_logger()
        self.chat = Chat()
        self.tg = Telegram()
        self.n_p = NowPayments()
        self.vpn_manager = VPNKeyManager()
        self.bot = self.tg.bot

    async def distribution(self, data) -> None:
        update = self.tg.create_update(data=data)
        if update.message:
            if update.message.entities:
                for entity in update.message.entities:
                    if entity.type == "bot_command":
                        self.logger.info(
                            f"user id - {update.message.from_user.id} username - {update.message.from_user.first_name} bot command - {update.message.text}")
                        await self.commands(update=update)
            else:
                self.logger.info(f"user id - {update.message.from_user.id} recieved message: {update.message.text}")
                await self.messages(update=update)

        if update.callback_query:
            await self.callback(update=update)

    async def remove_keyboard(self, update: Update, type: str) -> None:
        if type == 'callback':
            try:
                await self.bot.edit_message_reply_markup(
                    chat_id=update.callback_query.message.chat_id,
                    message_id=update.callback_query.message.message_id,
                    reply_markup=None
                )
            except Exception as e:
                self.logger.warn(f'There is no reply markup for delete: {e}')
        elif type == 'message':
            try:
                await self.bot.edit_message_reply_markup(
                    chat_id=update.message.chat_id,
                    message_id=update.message.message_id,
                    reply_markup=ReplyKeyboardRemove()
                )
            except Exception as e:
                self.logger.warn(f'There is no reply markup for delete: {e}')

    async def commands(self, update: Update) -> None:
        await self.remove_keyboard(update, 'message')
        if update.message.text == "/start":
            self.logger.info(f'command start send')
            user = user_repository.update_or_create_user(tg_id=update.message.from_user.id,
                                                         first_name=update.message.from_user.first_name)
            self.logger.info(f'User: {user}')
            await self.tg.bot.send_message(
                chat_id=update.message.chat_id,
                text=self.chat.start_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.chat.start_keyboard()
            )

    async def messages(self, update: Update) -> None:
        await self.remove_keyboard(update, 'message')
        await self.tg.bot.send_message(
            chat_id=update.message.chat_id,
            text=self.chat.default,
        )

    async def callback(self, update: Update) -> None:
        await self.remove_keyboard(update, 'callback')
        callback_data = update.callback_query.data

        if callback_data == "user_keys":
            self.logger.info(f'callback user_keys send')
            user = user_repository.get_user_by_tg_id(tg_id=update.callback_query.from_user.id)
            keys = vpn_keys_repository.get_vpn_keys_by_user_id(user_id=user.id)
            if not keys:
                message = "У вас нет активных VPN-ключей."
            else:
                message = "***Ваши VPN-ключи***\n\n"
                for key in keys:
                    key_info = f"🔑 ***Ключ:*** ```{self.vpn_manager.generate_vless_link(key.uuid, key.client_id)}```\n📅 ___Дата окончания: {key.expires_at.strftime('%d.%m.%Y')}___\n\n"
                    message += key_info
            await self.tg.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.chat.start_keyboard()
            )
        elif callback_data == "instruction":
            message = f"***Инструкция***"
            await self.tg.bot.send_video(
                chat_id=update.callback_query.message.chat_id,
                video=open((self.chat.base_dir + self.chat.video_instruction), 'rb'),
                caption=message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.chat.start_keyboard()
            )
        elif callback_data == "user_balance":
            self.logger.info(f'callback user_balance send')
            user = user_repository.get_user_by_tg_id(tg_id=update.callback_query.from_user.id)
            message = f"***Ваш баланс:*** {round(user.balance, 4)} USD"
            await self.tg.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.chat.start_keyboard()
            )
        elif callback_data == "user_top_up":
            message = "***Выберите монету пополнения***"
            await self.tg.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.chat.top_up_currency_keyboard()
            )
        elif callback_data.startswith("top_up_") and len(callback_data.split('_')) == 3:
            currency = callback_data.split('_')[-1]
            message = f"***Выберите сумму пополнения в {currency.upper()}***"
            await self.tg.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.chat.amount_keyboard(currency)
            )
        elif callback_data.startswith("top_up_") and len(callback_data.split('_')) == 4:
            currency = callback_data.split('_')[2]
            amount = int(callback_data.split('_')[-1])

            self.logger.info(f'callback {callback_data} send')
            user = user_repository.get_user_by_tg_id(tg_id=update.callback_query.from_user.id)

            if currency.upper() == "USDT":
                pay_currency = "USDTTRC20"
            else:
                pay_currency = currency.upper()

            current_datetime = datetime.now().strftime("%H%M%S_%m%d")

            try:
                invoice = self.n_p.create_invoice(
                    amount=amount,
                    currency="USD",
                    order_id=f"order_{user.tg_id}_{currency}_{amount}_{current_datetime}",
                    pay_currency=pay_currency
                )

                self.logger.info(f"Созданный инвойс:\n{json.dumps(invoice, indent=4, ensure_ascii=False)}")

                invoice_url = invoice.get('invoice_url', None)

                if invoice_url:
                    await self.tg.bot.send_message(
                        chat_id=update.callback_query.message.chat_id,
                        text=f"Перейдите по ссылке для оплаты: {invoice_url}",
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=self.chat.start_keyboard()
                    )
                else:
                    raise ValueError("Не удалось получить ссылку на оплату. Проверьте ответ API.")

            except Exception as e:
                self.logger.error(f'Ошибка при создании инвойса: {str(e)}')
                await self.tg.bot.send_message(
                    chat_id=update.callback_query.message.chat_id,
                    text="Произошла ошибка при создании инвойса. Попробуйте позже.",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self.chat.start_keyboard()
                )
        elif callback_data == "user_create_key":
            message = "***Выберите тарифный план***"
            await self.tg.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.chat.subscription_keyboard()
            )
        elif callback_data.startswith("subscribe_"):
            user = user_repository.get_user_by_tg_id(tg_id=update.callback_query.from_user.id)

            if callback_data == "subscribe_day":
                price = 0.5
                period = "День"
                expiration_time = int((datetime.now() + timedelta(days=1)).timestamp() * 1000)
                gb_limit = 50
            elif callback_data == "subscribe_month":
                price = 4.8
                period = "Месяц"
                expiration_time = int((datetime.now() + timedelta(days=30)).timestamp() * 1000)
                gb_limit = 1000
            elif callback_data == "subscribe_3_months":
                price = 13.5
                period = "3 месяца"
                expiration_time = int((datetime.now() + timedelta(days=90)).timestamp() * 1000)
                gb_limit = 3000
            elif callback_data == "subscribe_year":
                price = 129.6
                period = "Год"
                expiration_time = int((datetime.now() + timedelta(days=365)).timestamp() * 1000)
                gb_limit = 12000
            else:
                self.logger.error(f"Неподдерживаемый тариф: {callback_data}")
                return

            if user.balance < price:
                await self.tg.bot.send_message(
                    chat_id=update.callback_query.message.chat_id,
                    text="***Недостаточно средств на балансе для покупки этого тарифа.***\n___Пополните баланс.___",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self.chat.start_keyboard()
                )
                return

            try:
                print(f"gb_limit: {gb_limit}, type: {type(gb_limit)}")
                print(f"expiration_time: {expiration_time}, type: {type(expiration_time)}")
                vpn_key = self.vpn_manager.create_vpn_client(user=user, expiration_time=expiration_time, gb_limit=gb_limit)
                user_repository.update_user_balance(user.id, user.balance - price)

                await self.tg.bot.send_message(
                    chat_id=update.callback_query.message.chat_id,
                    text=f"🔑 Ваш VPN ключ для периода {period}: ```{vpn_key}```\n\nКлюч будет действителен до {datetime.fromtimestamp(expiration_time / 1000).strftime('%d.%m.%y %H:%M')}",
                    parse_mode=ParseMode.MARKDOWN,
                )
                await self.tg.bot.send_message(
                    chat_id=update.callback_query.message.chat_id,
                    text=f"Теперь скачайте приложение для IPhone или Android и добавьте в него свой ключ.\n\n"
                         f"Вмдео-инструкция и приложения:",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self.chat.apps_keyboard()
                )

                self.logger.info(
                    f"Пользователь {user.tg_id} приобрел ключ на {period}. Новый баланс: {user.balance - price} USD")

            except Exception as e:
                self.logger.error(f"Ошибка при создании VPN ключа: {str(e)}")
                await self.tg.bot.send_message(
                    chat_id=update.callback_query.message.chat_id,
                    text="Произошла ошибка при создании VPN ключа. Попробуйте позже.",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self.chat.start_keyboard()
                )
