import re
from django.db.models import Q
from users.models import CustomUser
from orders_bot.dispatcher import dp
from orders_bot.buttons.reply import *
from orders_bot.buttons.inline import *
from aiogram.filters import StateFilter
from orders_bot.state import RegisterState
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from orders_bot.utils import format_phone_number, is_valid_full_name

@dp.message(StateFilter(RegisterState.first_name))
async def process_first_name(message: Message, state: FSMContext):
    first_name = message.text.strip()

    if not is_valid_full_name(first_name):
        await message.answer("Iltimos, faqat harflardan iborat bo'lgan haqiqiy ism kiriting:")
        return

    await state.update_data(first_name=first_name)
    await message.answer("Iltimos, familiyangizni kiriting:")
    await state.set_state(RegisterState.last_name)



@dp.message(StateFilter(RegisterState.last_name))
async def process_last_name(message: Message, state: FSMContext):
    last_name = message.text.strip()

    if not is_valid_full_name(last_name):
        await message.answer("Iltimos, faqat harflardan iborat bo'lgan haqiqiy familiya kiriting:")
        return

    await state.update_data(last_name=last_name)
    await message.answer(
        "📞 Telefon raqamingizni Raqamni yuborish tugmasi orqali yuboring yoki +998900000000 formatida kiriting:",
        reply_markup=phone_number_btn()
    )
    await state.set_state(RegisterState.phone_number)



@dp.message(StateFilter(RegisterState.phone_number))
async def process_phone_number(message: Message, state: FSMContext):

    # Orqaga qaytish
    if message.text == "🔙 Orqaga":
        await state.set_state(RegisterState.last_name)
        await message.answer("Iltimos, familiyangizni kiriting:", reply_markup=back())
        return

    phone_number = None
    if message.contact:
        phone_number = format_phone_number(message.contact.phone_number)

    
    elif message.text and re.match(r"^\+\d{9,13}$", message.text):
        phone_number = format_phone_number(message.text)


    if not phone_number:
        await message.answer(
            "❗️ Noto‘g‘ri format!\nTelefon raqamingizni Raqamni yuborish 📞 tugmasi orqali yuboring yoki +998900000000 formatida kiriting:",
            reply_markup=phone_number_btn()
        )
        return

    await state.update_data(phone_number=phone_number)

    await state.set_state(RegisterState.address)
    await message.answer(
        "🏠 Yashash manzilingizni kiriting yoki joylashuv yuborish tugmasidan foydalaning:",
        reply_markup=get_location_keyboard()
    )


@dp.message(StateFilter(RegisterState.address))
async def user_address_get(message: Message, state: FSMContext):

    data = await state.get_data()
    tg_id = message.from_user.id

    is_location = False
    lat = None
    lon = None
    location_text = None

    if message.location:
        is_location = True
        lat = message.location.latitude
        lon = message.location.longitude
    else:
        location_text = message.text.strip()

    user = CustomUser.objects.filter(Q(phone_number=data['phone_number']) | Q(tg_id=tg_id) | Q(username=message.from_user.username)).first()

    if user:
        user.username = message.from_user.username or ""
        user.tg_id = tg_id
        user.first_name = data['first_name']
        user.last_name = data['last_name']

        if is_location:
            user.lat = lat
            user.lang = lon
        else:
            user.address = location_text

        user.save()

    else:
        user = CustomUser.objects.create(
            tg_id=tg_id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=data['phone_number'],
            username=message.from_user.username or "",
            address=location_text if not is_location else "",
            lat=lat if is_location else None,
            lang=lon if is_location else None,
        )

    if not message.location:
        await message.delete()

    await state.clear()

    await message.answer("✅ Manzilingiz muvaffaqiyatli saqlandi.", reply_markup=ReplyKeyboardRemove())
    await message.answer("🛒 Do'konga kirish uchun pastdagi tugmalardan foydalaning.", reply_markup=main_menu_keyboard(user))
