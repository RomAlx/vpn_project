from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.constants import ParseMode

from backend.objects.VPNKeyManager import VPNKeyManager
from backend.repositories.vpn_keys_repository import VPNKeysRepository
from backend.repositories.user_repository import UserRepository
from backend.routes.api import telegram_controller


class VPNNotificationService:
    def __init__(self):
        self.vpn_keys_repo = VPNKeysRepository()
        self.vpn_manager = VPNKeyManager()
        self.user_repo = UserRepository()
        self.tg = telegram_controller.tg
        self.scheduler = AsyncIOScheduler()

    async def check_and_notify(self):
        print('start checking VPN keys')
        current_time = datetime.utcnow()
        expiration_threshold = current_time + timedelta(hours=1)
        keys_expiring_soon = self.vpn_keys_repo.get_keys_expiring_soon(expiration_threshold)
        print('keys_expiring_soon:\n', keys_expiring_soon)
        for key in keys_expiring_soon:
            user = self.user_repo.get_user_by_id(key.user_id)
            if user and user.tg_id:
                message = (
                    f""
                    f"🔑 Ваш VPN ключ истекает меньше чем через час.\n "
                    f"```{self.vpn_manager.generate_vless_link(key.uuid, key.client_id)}```\n"
                    f"📅 ___Дата окончания: {key.expires_at.strftime('%d.%m.%Y %H:%m')}___\n\n"
                )
                await self.tg.bot.send_message(
                    chat_id=user.tg_id,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN
                )
        print('end checking VPN keys')

    def start(self):
        self.scheduler.add_job(self.check_and_notify, 'interval', hours=1)
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown()
