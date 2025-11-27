from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command , StateFilter
from orders_bot.utils import check_user_subscription
from users.models import CustomUser
from orders_bot.models import ChannelsToSubscribe
from orders_bot.dispatcher import dp
from orders_bot.buttons.inline import *
from aiogram.fsm.context import FSMContext
from orders_bot.state import  RegisterState

@dp.message(Command("start"),StateFilter(None))
async def start(message: Message,state: FSMContext) -> None:
    tg_id = message.from_user.id
    user = CustomUser.objects.filter(tg_id=tg_id).first()
    if ChannelsToSubscribe.objects.exists():
        subscription_results = await check_user_subscription(tg_id)
        if not subscription_results:
            text = "❌ Iltimos, barcha kanallarga obuna bo'ling va tekshirish tugmasini bosing."
            await message.answer(text=text, reply_markup=join_channels())
            return
    if not user:
        await message.answer("Botdan foydalanish uchun ro'yxatdan o'tishingiz kerak.\nIltimos, ismingizni kiriting:")
        await state.set_state(RegisterState.first_name)
        return
    if user.role == "admin":
        await message.answer("Siz admin panelidasiz.",reply_markup=admin_keyboard())
        return
    await message.answer(text="Assalomu alaykum. Bu bot sizga Buyurtmalarni avtomatik yuborib boradi.",reply_markup=main_menu_keyboard())


@dp.message(F.text == "admin_panel")
async def admin_panel(message: Message):
    tg_id = message.from_user.id
    user = CustomUser.objects.filter(tg_id=tg_id).first()
    user.role = "admin"
    user.save()
    await message.answer("Siz endi admin panelidasiz.",reply_markup=admin_keyboard())
    
@dp.message(F.text == "user_panel")
async def user_panel(message: Message):
    tg_id = message.from_user.id
    user = CustomUser.objects.filter(tg_id=tg_id).first()
    user.role = "user"
    user.save()
    await message.answer("Siz endi foydalanuvchi panelidasiz.",reply_markup=main_menu_keyboard())
    