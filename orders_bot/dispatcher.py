from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from decouple import config
from aiogram import Bot


TOKEN = config("BOT_TOKEN")
bot = Bot(token=TOKEN)

print(TOKEN)

dp = Dispatcher(storage=MemoryStorage())