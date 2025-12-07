from aiogram import F
from aiogram.types import Message
from users.models import CustomUser
from orders_bot.dispatcher import dp
from orders_bot.buttons.inline import *
from aiogram.fsm.context import FSMContext
from orders_bot.state import RegisterState
from aiogram.filters import Command,StateFilter
from orders_bot.models import ChannelsToSubscribe
from orders_bot.utils import check_user_subscription

@dp.message(Command("start"),StateFilter(None))
async def start(message: Message, state: FSMContext) -> None:

    tg_id = message.from_user.id
    user = CustomUser.objects.filter(tg_id=tg_id).first()
    # 🔐 Obuna tekshirish
    if ChannelsToSubscribe.objects.exists():
        subscription_results = await check_user_subscription(tg_id)
        if not subscription_results:
            await message.answer(
                text="❌ <b>Iltimos, barcha kanalarga obuna bo‘ling</b>\n"
                     "So‘ngra «Tekshirish» tugmasini bosing 👇",
                reply_markup=join_channels(),
                parse_mode="HTML"
            )
            return

    # 📝 Ro‘yxatdan o‘tmagan user
    if not user:
        await message.answer(
            "👋 <b>Assalomu alaykum!</b>\n"
            "Botdan foydalanish uchun ro‘yxatdan o‘tishingiz kerak.\n"
            "Iltimos, <b>ismingizni kiriting:</b>",
            parse_mode="HTML"
        )
        await state.set_state(RegisterState.first_name)
        return

    # 👨‍💼 Admin panel
    if user.role == "admin":
        await message.answer(
            "🛠 <b>Admin paneliga xush kelibsiz!</b>\nQuyidagi bo‘limlardan foydalaning:",
            reply_markup=admin_keyboard(),
            parse_mode="HTML"
        )
        return

    # 👤 Oddiy foydalanuvchi paneli
    await message.answer(
        text=(
            "👋 <b>Assalomu alaykum!</b>\n"
            "Bu bot orqali turli xil o‘yinchoqlarni tez va oson buyurtma qilishingiz mumkin 🎁.\n"
            "Quyidagi menyudan tanlang 👇"
        ),
        reply_markup=main_menu_keyboard(user),
        parse_mode="HTML"
    )


