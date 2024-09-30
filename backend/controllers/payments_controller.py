# app/controllers/app_controller.py

from fastapi import HTTPException
from ..logs.logger import Logger
from backend.repositories.user_repository import UserRepository as user_repository
from ..controllers.telegram_controller import TelegramController as telegram_controller

logger = Logger(name="controller.app").get_logger()


class PaymentController:
    def __init__(self, bot):
        self.bot = bot

    async def handle_payment_success(self, order_id: str, amount: float):
        try:
            # Извлекаем tg_id из order_id
            order_id_parts = order_id.split('_')
            tg_id = int(order_id_parts[1])

            # Поиск пользователя по tg_id
            user = user_repository.get_user_by_tg_id(tg_id=tg_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Обновление баланса пользователя
            new_balance = user.balance + amount
            user_repository.update_user_balance(user.id, new_balance)

            # Отправка уведомления пользователю
            await self.bot.send_message(
                chat_id=user.tg_id,
                text=f"✅ Оплата на сумму {amount} USD была успешно завершена! Ваш новый баланс: {new_balance} USD."
            )

            logger.info(f"Баланс пользователя {user.tg_id} обновлен на сумму {amount}. Новый баланс: {new_balance} USD")
        except Exception as e:
            logger.error(f"Ошибка при обработке успешного платежа: {str(e)}")
            raise HTTPException(status_code=500, detail="Ошибка при обработке успешного платежа")

    async def handle_payment_cancel(self, order_id: str):
        try:
            # Извлекаем tg_id из order_id
            order_id_parts = order_id.split('_')
            tg_id = int(order_id_parts[1])

            # Поиск пользователя по tg_id
            user = user_repository.get_user_by_tg_id(tg_id=tg_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Отправка уведомления пользователю об отмене
            await bot.send_message(
                chat_id=user.tg_id,
                text="❌ Оплата была отменена. Если это ошибка, попробуйте снова."
            )

            logger.info(f"Отправлено уведомление об отмене оплаты для пользователя {user.tg_id}")
        except Exception as e:
            logger.error(f"Ошибка при обработке отмены платежа: {str(e)}")
            raise HTTPException(status_code=500, detail="Ошибка при обработке отмены платежа")

    async def handle_payment_error(self, order_id: str):
        try:
            # Извлекаем tg_id из order_id
            order_id_parts = order_id.split('_')
            tg_id = int(order_id_parts[1])

            # Поиск пользователя по tg_id
            user = user_repository.get_user_by_tg_id(tg_id=tg_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Отправка уведомления пользователю об ошибке
            await self.bot.send_message(
                chat_id=user.tg_id,
                text="⚠️ Произошла ошибка при обработке вашего платежа. Пожалуйста, свяжитесь с поддержкой."
            )

            logger.info(f"Отправлено уведомление об ошибке оплаты для пользователя {user.tg_id}")
        except Exception as e:
            logger.error(f"Ошибка при обработке ошибки платежа: {str(e)}")
            raise HTTPException(status_code=500, detail="Ошибка при обработке ошибки платежа")
