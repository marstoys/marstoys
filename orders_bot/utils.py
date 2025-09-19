from aiogram.types import  BotCommand


async def set_bot_commands(bot):
    commands = [
        BotCommand(command="start", description="🚀 Botni ishga tushirish"),
        BotCommand(command="all", description="📑 Barcha zayafkalarni ko‘rish"),
    ]
    await bot.set_my_commands(commands)
