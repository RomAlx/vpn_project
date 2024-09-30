import asyncio
import json
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from ..logs.logger import Logger
from ..controllers.telegram_controller import TelegramController as telegram_controller
from ..controllers.payments_controller import PaymentController as payments_controller

from backend.repositories.user_repository import UserRepository as user_repository

router = APIRouter()
logger = Logger(name="routes.api").get_logger()
telegram_controller = telegram_controller()
payments_controller = payments_controller(telegram_controller.bot)


@router.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        formatted_json = json.dumps(data, indent=4, ensure_ascii=False, sort_keys=True)
        logger.info(f"Received:\n{formatted_json}")
        await telegram_controller.distribution(data)
        return {"ok": "200"}
    except Exception as e:
        logger.error(f"Ошибка в обработке вебхука Telegram: {str(e)}")
        return {"error": str(e)}


@router.post("/payment/callback")
async def payment_ipn_callback(request: Request):
    try:
        data = await request.json()
        order_id = data.get('order_id')
        payment_status = data.get('payment_status')
        actual_amount_received = data.get('actual_amount_received')

        if not order_id:
            raise HTTPException(status_code=400, detail="Missing order_id in request")

        if payment_status == "finished":
            logger.info(f"Payment success for order_id: {order_id}")
            await payments_controller.handle_payment_success(order_id, actual_amount_received)
        elif payment_status == "failed" or payment_status == "cancelled":
            logger.info(f"Payment cancel for order_id: {order_id}")
            await payments_controller.handle_payment_cancel(order_id)
        else:
            logger.warning(f"Payment error for order_id: {order_id} with status: {payment_status}")
            await payments_controller.handle_payment_error(order_id)

        return JSONResponse(status_code=200, content={"status": "ok"})
    except Exception as e:
        logger.error(f"Error in payment IPN callback processing: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing payment IPN callback")
