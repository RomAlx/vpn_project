# api.py

import asyncio
import json
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from ..logs.logger import Logger
from ..controllers.telegram_controller import TelegramController as telegram_controller
from ..controllers.payments_controller import PaymentController as payments_controller
from backend.repositories.user_repository import UserRepository as user_repository
from ..objects.NowPayments import NowPayments

router = APIRouter()
logger = Logger(name="routes.api").get_logger()
telegram_controller = telegram_controller()
payments_controller = payments_controller(telegram_controller.bot)
nowpayments = NowPayments()


@router.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    """
    Обработка вебхуков от Telegram
    """
    try:
        data = await request.json()
        formatted_json = json.dumps(data, indent=4, ensure_ascii=False, sort_keys=True)
        logger.info(f"Received Telegram webhook:\n{formatted_json}")

        await telegram_controller.distribution(data)
        return JSONResponse(status_code=200, content={"status": "ok"})

    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {str(e)}")
        return JSONResponse(status_code=200, content={"status": "error", "message": str(e)})


@router.post("/payment/callback")
async def payment_ipn_callback(request: Request):
    """Обработка IPN-уведомлений от NOWPayments"""
    try:
        # Получаем raw body для проверки подписи
        body = await request.body()
        headers = dict(request.headers)

        logger.info(f"Received payment callback:")
        logger.info(f"Headers: {json.dumps(headers)}")
        logger.info(f"Body: {body.decode()}")

        # Проверяем подпись только если не в sandbox режиме
        signature = headers.get('x-nowpayments-sig')
        if not nowpayments.is_sandbox and not signature:
            logger.error("Missing signature in headers")
            return JSONResponse(
                status_code=200,
                content={"status": "error", "message": "Missing signature"}
            )

        if not nowpayments.is_sandbox and not nowpayments.verify_nowpayments_signature(body, signature):
            logger.error(f"Invalid signature. Received: {signature}")
            return JSONResponse(
                status_code=200,
                content={"status": "error", "message": "Invalid signature"}
            )

        data = await request.json()
        logger.info(f"Processing payment data: {json.dumps(data, indent=2)}")

        # В sandbox режиме payment_id может прийти как token_id
        payment_id = data.get('payment_id') or data.get('token_id')
        order_id = data.get('order_id')
        payment_status = data.get('payment_status')
        price_amount = float(data.get('price_amount', 0))

        if not all([order_id, payment_status]):
            logger.error(f"Missing required fields. Data: {data}")
            return JSONResponse(
                status_code=200,
                content={"status": "error", "message": "Missing required fields"}
            )

        # Обработка различных статусов
        try:
            if payment_status == "finished":
                logger.info(f"Payment success: order_id={order_id}, amount={price_amount}")
                await payments_controller.handle_payment_success(order_id, price_amount)

            elif payment_status == "partially_paid":
                logger.warning(f"Partial payment: order_id={order_id}")
                await payments_controller.handle_payment_error(order_id)

            elif payment_status in ["failed", "expired", "refunded", "cancelled"]:
                logger.info(f"Payment {payment_status}: order_id={order_id}")
                await payments_controller.handle_payment_cancel(order_id)

            elif payment_status in ["waiting", "confirming", "confirmed", "sending"]:
                logger.info(f"Payment in progress: {payment_status} for order_id={order_id}")

            else:
                logger.warning(f"Unknown payment status: {payment_status} for order_id={order_id}")
                await payments_controller.handle_payment_error(order_id)

            return JSONResponse(status_code=200, content={"status": "ok"})

        except Exception as process_error:
            logger.error(f"Error processing payment status: {str(process_error)}")
            # Всегда возвращаем 200, даже при ошибках
            return JSONResponse(
                status_code=200,
                content={"status": "error", "message": str(process_error)}
            )

    except Exception as e:
        logger.error(f"Error in payment callback handler: {str(e)}")
        # Всегда возвращаем 200 для NOWPayments
        return JSONResponse(
            status_code=200,
            content={"status": "error", "message": str(e)}
        )