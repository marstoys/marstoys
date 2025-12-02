from aiogram import F
from shop.models import Cart
from users.models import CustomUser
from orders_bot.state import OrderState
from aiogram.types import CallbackQuery
from orders_bot.buttons.inline import *
from orders_bot.dispatcher import dp,bot
from aiogram.fsm.context import FSMContext
from orders_bot.state import RegisterState
from orders_bot.utils import check_user_subscription


@dp.callback_query(F.data == "back")
async def back_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    user = CustomUser.objects.filter(tg_id=callback_query.from_user.id).first()
    if user and user.role == "user":
        await callback_query.message.edit_text(text="Asosiy menu",reply_markup=main_menu_keyboard(user))
        return
    await callback_query.message.edit_text(text="Assalomu alaykum. Bu bot sizga Buyurtmalarni avtomatik yuborib boradi.",reply_markup=admin_keyboard())
    data = await state.get_data()
    message_ids = data.get("message_ids", [])

    for msg_id in message_ids:
        try:
            await bot.delete_message(
                chat_id=callback_query.message.chat.id,
                message_id=msg_id
            )
        except Exception:
            pass
    await state.clear()



@dp.callback_query(F.data == "check_order_number")
async def order_number_handler(callback_query: CallbackQuery, state: FSMContext):
    msg = await callback_query.message.edit_text(text="Iltimos, buyurtma raqamini kiriting:", reply_markup=back_keyboard())
    await state.update_data(msg=msg.message_id)
    await state.set_state(OrderState.waiting_for_order_number)


@dp.callback_query(F.data == "check_subscription")
async def check_subscription(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer()
    await callback.message.edit_text(text="🔄 Obunalar tekshirilmoqda...",reply_markup=None)
    subscription_results = await check_user_subscription(user_id)
    if not subscription_results:
        text = "❌ Iltimos, barcha kanallarga obuna bo'ling va tekshirish tugmasini bosing."
        await callback.message.edit_text(text=text, reply_markup=join_channels())
        return
    user = CustomUser.objects.filter(tg_id=user_id).first()
    await callback.message.edit_text(text="✅ Botdan foydalanishingiz mumkin.", reply_markup=main_menu_keyboard(user))



@dp.callback_query(F.data == "view_cart")
async def view_cart_handler(callback_query: CallbackQuery, state: FSMContext):
    user = CustomUser.objects.filter(tg_id=callback_query.from_user.id).first()
    if not user:
        await callback_query.message.edit_text("Botdan foydalanish uchun ro'yxatdan o'tishingiz kerak.\nIltimos, ismingizni kiriting:",reply_markup=None)
        await state.set_state(RegisterState.first_name)
        return
    orders = Cart.objects.filter(user_id=user.id).select_related('product')
    if not orders.exists():
        await callback_query.message.edit_text("🛒 Sizning savatchingiz bo'sh.", reply_markup=back_keyboard())
        return
    text = "🛒 Sizning savatchangizdagi buyurtmalar:\n\n"
    total_price = 0
    for i, order in enumerate(orders):
        total_price += order.price * order.quantity
        text += f"{i+1}. {order.product.name} - {order.color} - {order.quantity} ta - {order.price} \n"
    text += f"\nJami: {total_price} so'm"
    await callback_query.message.edit_text(text, reply_markup=cart_keyboard())
        
@dp.callback_query(F.data == "clear_cart")
async def clear_cart_handler(callback_query: CallbackQuery, state: FSMContext):
    user = CustomUser.objects.filter(tg_id=callback_query.from_user.id).first()
    if not user:
        await callback_query.message.edit_text("Botdan foydalanish uchun ro'yxatdan o'tishingiz kerak.\nIltimos, ismingizni kiriting:",reply_markup=None)
        await state.set_state(RegisterState.first_name)
        return
    Cart.objects.filter(user_id=user.id).delete()
    await callback_query.message.edit_text("🛒 Sizning savatchingiz tozalandi.", reply_markup=back_keyboard())

@dp.callback_query(F.data == "view_profile")
async def view_profile_handler(callback_query: CallbackQuery, state: FSMContext):
    user = CustomUser.objects.filter(tg_id=callback_query.from_user.id).first()
    if not user:
        await callback_query.message.edit_text("Botdan foydalanish uchun ro'yxatdan o'tishingiz kerak.\nIltimos, ismingizni kiriting:",reply_markup=None)
        await state.set_state(RegisterState.first_name)
        return
    text = (
        f"👤 <b>Profil ma'lumotlari:</b>\n\n"
        f"Username: @{callback_query.from_user.username if callback_query.from_user.username else 'Kiritilmagan'}\n"
        f"Ism: {user.first_name if user.first_name else "Kiritilmagan"} \n"
        f"Familiya: {user.last_name if user.last_name else 'Kiritilmagan'}\n"
        f"Telefon raqam: {user.phone_number if user.phone_number else 'Kiritilmagan'}\n"
        
    )
    await callback_query.message.edit_text(text, reply_markup=change_info_keyboard())
    

    
@dp.callback_query(F.data == "view_info")
async def view_info_handler(callback_query: CallbackQuery):
    await callback_query.message.edit_text(text="Kerakli bo'limni tanlang ⬇️", reply_markup=info_keyboard())
    

@dp.callback_query(F.data == "change_profile_info")
async def change_profile_info_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Iltimos, ismingizni kiriting:")
    await state.set_state(RegisterState.first_name)
    return


@dp.callback_query(F.data == "leave_comment")
async def leave_comment_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Iltimos, izohingizni kiriting:")
    await state.set_state(OrderState.leave_feedback)
    return


@dp.callback_query(F.data == "delivery_terms")
async def delivery_terms_handler(callback_query: CallbackQuery):
    text = (
        "🚚 <b>Yetkazib berish shartlari:</b>\n\n"
        "1. Buyurtmalar 1-3 ish kuni ichida yetkazib beriladi.\n"
        "2. Yetkazib berish narxi manzilga qarab o'zgaradi.\n"
        "3. Buyurtma tasdiqlangandan so'ng, bekor qilish mumkin emas.\n"
        "4. Qo'shimcha ma'lumot uchun biz bilan bog'laning."
    )
    await callback_query.message.edit_text(text, reply_markup=back_keyboard())


@dp.callback_query(F.data == "contacts")
async def contacts_handler(callback_query: CallbackQuery):
    text = (
        "☎️ <b>Kontaktlar:</b>\n\n"
        "Telefon: +998 91 487 21 12\n"
        "Email: eldorbekjuraev1993@gmail.com\n"
        "Manzil: Andijon, Jaxon Bozor\nO‘rikzor bozori, Gilam bozor / Samarbonu 39A/1")
    await callback_query.message.edit_text(text, reply_markup=back_keyboard())
    

    