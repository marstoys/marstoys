import logging
import sys
import asyncio
from django.core.management.base import BaseCommand
from orders_bot.handlers import *
from orders_bot.dispatcher import bot,  dp
from orders_bot.utils import set_bot_commands

# Set the default settings module for your Django project
async def main() -> None:
    await set_bot_commands()
    await dp.start_polling(bot)



class Command(BaseCommand):

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())