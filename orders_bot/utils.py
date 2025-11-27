import re
from aiogram.types import ChatMember
from aiogram.types import BotCommand
from aiogram.enums import ChatMemberStatus
from orders_bot.models import ChannelsToSubscribe
from orders_bot.dispatcher import bot



async def set_bot_commands():
    commands = [
        BotCommand(command="start", description="🚀 Botni ishga tushirish"),
    ]
    await bot.set_my_commands(commands)




def format_phone_number(phone_number: str) -> str | bool:
    phone_number = ''.join(c for c in phone_number if c.isdigit())

    # Prepend +998 if missing
    if phone_number.startswith('998'):
        return phone_number
    elif not phone_number.startswith('998') and len(phone_number) == 9:
        phone_number = '998' + phone_number

    # Check final phone number length
    if len(phone_number) == 12:
        return phone_number
    else:
        return False

def is_valid_full_name(full_name: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ' -]+", full_name))


async def check_user_subscription(user_id: int) -> bool:
    results = {}
    chat_ids = list(ChannelsToSubscribe.objects.values_list("link", flat=True))
    for chat_id in chat_ids:
        try:
            chat_member: ChatMember = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
            subscribed_statuses = {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR}
            results[chat_id] = chat_member.status in subscribed_statuses
        except Exception as e:
            print(f"❌ Error checking {chat_id}: {e}")
            results[chat_id] = False

    return all(results.values())



def remove_at_prefix(text: str) -> str:
    return text.lstrip('@')

