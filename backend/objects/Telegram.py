import os
from dotenv import load_dotenv
from queue import Queue

from telegram.ext import Application, CommandHandler, MessageHandler
from telegram import Bot, Update


class Telegram:
    def __init__(self):
        load_dotenv()
        self.queue = Queue()
        self.token = os.getenv('TELEGRAM_BOT_API_TOKEN')
        self.webhook = os.getenv('PROJECT_URL') + '/api/telegram/webhook'
        self.application = Application.builder().token(self.token).updater(None).build()
        self.bot = self.application.bot

    async def set_webhook(self):
        await self.application.bot.deleteWebhook()
        status = await self.application.bot.set_webhook(url=self.webhook, allowed_updates=Update.ALL_TYPES)
        print('Token: ', self.token)
        print('Webhook url: ', self.webhook)
        print('Webhook status: {}'.format(status))

    def create_update(self, data: dict) -> Update:
        update = Update.de_json(data=data, bot=self.bot)
        return update
