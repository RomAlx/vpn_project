# app/controllers/payments_controller.py
from datetime import datetime

from fastapi import HTTPException
from telegram.constants import ParseMode
from ..logs.logger import Logger
from backend.repositories.user_repository import UserRepository as user_repository

logger = Logger(name="controller.payment").get_logger()


class PaymentController:
    def __init__(self, bot):
        self.bot = bot
        self.logger = logger

    async def handle_payment_success(self, order_id: str, amount: float):
        """
        Обработка успешного платежа

        Args:
            order_id (str): Идентификатор заказа
            amount (float): Сумма платежа в USD
        """
        try:
            self.logger.info(f"Processing successful payment: order_id={order_id}, amount={amount}")

            # Извлекаем tg_id из order_id
            try:
                order_id_parts = order_id.split('_')
                tg_id = int(order_id_parts[1])
            except (IndexError, ValueError) as e:
                self.logger.error(f"Invalid order_id format: {order_id}")
                raise ValueError(f"Invalid order_id format: {str(e)}")

            # Поиск пользователя
            user = user_repository.get_user_by_tg_id(tg_id=tg_id)
            if not user:
                self.logger.error(f"User not found: tg_id={tg_id}")
                raise HTTPException(status_code=404, detail="User not found")

            # Обновление баланса
            try:
                new_balance = round(user.balance + amount, 2)
                user_repository.update_user_balance(user.id, new_balance)
                self.logger.info(f"Balance updated for user {tg_id}: +{amount} USD, new balance: {new_balance} USD")
            except Exception as e:
                self.logger.error(f"Error updating balance: {str(e)}")
                raise

            # Отправка уведомления
            message = (
                f"✅ *Оплата успешно завершена!*\n\n"
                f"💰 Сумма: `{amount}` USD\n"
                f"💳 Новый баланс: `{new_balance}` USD"
            )

            await self.bot.send_message(
                chat_id=user.tg_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )

        except ValueError as ve:
            self.logger.error(f"Validation error in payment success handler: {str(ve)}")
            raise HTTPException(status_code=400, detail=str(ve))
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error processing successful payment: {str(e)}")
            raise HTTPException(status_code=500, detail="Error processing successful payment")

    async def handle_payment_cancel(self, order_id: str):
        """
        Обработка отмены платежа

        Args:
            order_id (str): Идентификатор заказа
        """
        try:
            self.logger.info(f"Processing payment cancellation: order_id={order_id}")

            # Извлекаем tg_id
            try:
                order_id_parts = order_id.split('_')
                tg_id = int(order_id_parts[1])
            except (IndexError, ValueError) as e:
                self.logger.error(f"Invalid order_id format: {order_id}")
                raise ValueError(f"Invalid order_id format: {str(e)}")

            # Поиск пользователя
            user = user_repository.get_user_by_tg_id(tg_id=tg_id)
            if not user:
                self.logger.error(f"User not found: tg_id={tg_id}")
                raise HTTPException(status_code=404, detail="User not found")

            # Отправка уведомления
            message = (
                "❌ *Платёж не удался*\n\n"
                "Возможные причины:\n"
                "• Отмена платежа\n"
                "• Истекло время ожидания\n"
                "• Технические проблемы\n\n"
                "_Попробуйте выполнить оплату снова или обратитесь в поддержку._"
            )

            await self.bot.send_message(
                chat_id=user.tg_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )

        except ValueError as ve:
            self.logger.error(f"Validation error in payment cancel handler: {str(ve)}")
            raise HTTPException(status_code=400, detail=str(ve))
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error processing payment cancellation: {str(e)}")
            raise HTTPException(status_code=500, detail="Error processing payment cancellation")

    async def handle_payment_error(self, order_id: str):
        """
        Обработка ошибки платежа

        Args:
            order_id (str): Идентификатор заказа
        """
        try:
            self.logger.info(f"Processing payment error: order_id={order_id}")

            # Извлекаем tg_id
            try:
                order_id_parts = order_id.split('_')
                tg_id = int(order_id_parts[1])
            except (IndexError, ValueError) as e:
                self.logger.error(f"Invalid order_id format: {order_id}")
                raise ValueError(f"Invalid order_id format: {str(e)}")

            # Поиск пользователя
            user = user_repository.get_user_by_tg_id(tg_id=tg_id)
            if not user:
                self.logger.error(f"User not found: tg_id={tg_id}")
                raise HTTPException(status_code=404, detail="User not found")

            # Отправка уведомления
            message = (
                "⚠️ *Ошибка при обработке платежа*\n\n"
                "Пожалуйста, напишите в поддержку и укажите:\n"
                f"• ID заказа: `{order_id}`\n"
                f"• Время платежа: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n\n"
                "_Мы поможем разобраться с проблемой._"
            )

            await self.bot.send_message(
                chat_id=user.tg_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )

        except ValueError as ve:
            self.logger.error(f"Validation error in payment error handler: {str(ve)}")
            raise HTTPException(status_code=400, detail=str(ve))
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error processing payment error: {str(e)}")
            raise HTTPException(status_code=500, detail="Error processing payment error")

    async def handle_payment_progress(self, order_id: str, status: str):
        """
        Обработка промежуточных статусов платежа

        Args:
            order_id (str): Идентификатор заказа
            status (str): Статус платежа
        """
        try:
            self.logger.info(f"Processing payment progress: order_id={order_id}, status={status}")

            # Извлекаем tg_id
            try:
                order_id_parts = order_id.split('_')
                tg_id = int(order_id_parts[1])
            except (IndexError, ValueError) as e:
                self.logger.error(f"Invalid order_id format: {order_id}")
                raise ValueError(f"Invalid order_id format: {str(e)}")

            # Поиск пользователя
            user = user_repository.get_user_by_tg_id(tg_id=tg_id)
            if not user:
                self.logger.error(f"User not found: tg_id={tg_id}")
                raise HTTPException(status_code=404, detail="User not found")

            # Статусы и их описания
            status_messages = {
                "waiting": "⏳ *Ожидание оплаты*\n\nОжидаем поступление средств...",
                "confirming": "🔄 *Подтверждение транзакции*\n\nОжидаем подтверждения сети...",
                "confirmed": "✔️ *Транзакция подтверждена*\n\nСредства поступили, обрабатываем платёж...",
                "sending": "📤 *Обработка платежа*\n\nЗавершаем операцию..."
            }

            message = status_messages.get(
                status,
                f"🔄 *Обработка платежа*\n\nСтатус: {status}"
            )

            await self.bot.send_message(
                chat_id=user.tg_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )

        except ValueError as ve:
            self.logger.error(f"Validation error in payment progress handler: {str(ve)}")
            raise HTTPException(status_code=400, detail=str(ve))
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error processing payment progress: {str(e)}")
            raise HTTPException(status_code=500, detail="Error processing payment progress")