import os
from dotenv import load_dotenv
from fastapi import FastAPI

from .routes.api import router as api
from .routes.api import telegram_controller
from backend.services.vpn_notification_service import VPNNotificationService

app = FastAPI()

tg = telegram_controller.tg

load_dotenv()
base_dir = os.getenv("BASE_DIR")

app.include_router(api, prefix="/api")


@app.on_event("startup")
async def startup_event():
    await tg.set_webhook()
    app.state.notification_service = VPNNotificationService()
    app.state.notification_service.start()


@app.on_event("shutdown")
def shutdown_event():
    app.state.notification_service.stop()
