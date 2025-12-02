import re
from aiogram.types import  Message
from users.models import CustomUser
from users.models import  CustomUser
from orders_bot.dispatcher import dp
from orders_bot.buttons.reply import *
from orders_bot.buttons.inline import *
from aiogram.filters import StateFilter
from orders_bot.state import RegisterState
from aiogram.fsm.context import FSMContext
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
    await message.answer("Telefon raqamingizni Raqamni yuborish 📞 tugmasi orqali yuboring \nyoki +998900000000 formatida kiriting: !",reply_markup=phone_number_btn())
    await state.set_state(RegisterState.phone_number)

@dp.message(StateFilter(RegisterState.phone_number))
async def process_phone_number(message: Message, state: FSMContext):
    await message.delete()
    if message.text == "🔙 Orqaga":
        await state.set_state(RegisterState.last_name)
        await message.answer(text="Iltimos, familiyangizni kiriting:", reply_markup=back())
        return
        
    if message.contact:
        phone_number = format_phone_number(message.contact.phone_number)
        if not phone_number:
            await message.answer(text="Telefon raqamingizni Raqamni yuborish 📞 tugmasi orqali yuboring \nyoki +998900000000 formatida kiriting: !", reply_markup=phone_number_btn())    
            return
    elif message.text and re.match(r"^\+\d{9,13}$", message.text):
        phone_number = format_phone_number(message.text)
        if not phone_number:
            await message.answer(text="Telefon raqamingizni Raqamni yuborish 📞 tugmasi orqali yuboring \nyoki +998900000000 formatida kiriting: !", reply_markup=phone_number_btn())    
            return
    else:
        await message.answer(text="Telefon raqamingizni Raqamni yuborish 📞 tugmasi orqali yuboring \nyoki +998900000000 formatida kiriting: !", reply_markup=phone_number_btn())
        return
    user = CustomUser.objects.filter(phone_number=phone_number).first()
    if user:
        user.username = message.from_user.username if message.from_user.username else ""
        user.tg_id = message.from_user.id
        user.first_name = (await state.get_data())['first_name']
        user.last_name = (await state.get_data())['last_name']
        user.save()
    else:
        user = CustomUser.objects.create(
        tg_id=message.from_user.id,
        first_name=(await state.get_data())['first_name'],
        last_name=(await state.get_data())['last_name'],
        phone_number=phone_number,
        username=message.from_user.username if message.from_user.username else ""
    )
    await message.answer(text="Ro'yxatdan muvaffaqiyatli o'tdingiz! Endi botdan foydalanishingiz mumkin.", reply_markup=main_menu_keyboard(user))
    