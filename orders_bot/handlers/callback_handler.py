from aiogram import F
from shop.models import Cart
from users.models import CustomUser
from orders_bot.state import OrderState, RegisterState
from aiogram.types import CallbackQuery
from orders_bot.buttons.inline import *
from orders_bot.dispatcher import dp, bot
from aiogram.fsm.context import FSMContext
from orders_bot.utils import check_user_subscription


@dp.callback_query(F.data == "back")
async def back_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    user = CustomUser.objects.filter(tg_id=callback_query.from_user.id).first()
    
    if user and user.role == "user":
        await callback_query.message.edit_text(
            text="📌 <b>Asosiy menyu</b>\nQuyidagi bo‘limlardan birini tanlang 👇",
            reply_markup=main_menu_keyboard(user)
        )
        

    # Admin panel
    elif user and user.role == "admin":
        await callback_query.message.edit_text(
        text=(
            "✨ <b>Assalomu alaykum, administrator!</b>\n\n"
            "📦 Ushbu bot orqali barcha buyurtmalarni boshqarishingiz, "
            "mijozlar faolligini kuzatishingiz va operativ ishlashingiz mumkin."
        ),
        reply_markup=admin_keyboard()
    )

    # Tozalash
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
    msg = await callback_query.message.edit_text(
        text="📦 <b>Buyurtma raqamini kiriting:</b>",
        reply_markup=back_keyboard()
    )
    await state.update_data(msg=msg.message_id)
    await state.set_state(OrderState.waiting_for_order_number)



@dp.callback_query(F.data == "check_subscription")
async def check_subscription(callback: CallbackQuery,state: FSMContext):
    user_id = callback.from_user.id
    await callback.answer()

    await callback.message.edit_text("🔄 <b>Obunalar tekshirilmoqda...</b>")

    subscription_results = await check_user_subscription(user_id)

    if not subscription_results:
        await callback.message.edit_text(
            text="❌ <b>Iltimos, barcha kanallarga obuna bo‘ling!</b>\n"
                 "Tayyor bo‘lsangiz, pastdagi «Tekshirish» tugmasini bosing 👇",
            reply_markup=join_channels()
        )
        return

    user = CustomUser.objects.filter(tg_id=user_id).first()
    if not user:
        await callback.message.edit_text(
            text="📝 Botdan foydalanish uchun ro‘yxatdan o‘ting.\n\n"
                 "Iltimos, <b>ismingizni kiriting:</b> 👇"
        )
        await state.set_state(RegisterState.first_name)
        return

    await callback.message.edit_text(
        text="✅ <b>Obuna muvaffaqiyatli tasdiqlandi!</b>\nBotdan bemalol foydalanishingiz mumkin 😎",
        reply_markup=main_menu_keyboard(user)
    )



@dp.callback_query(F.data == "view_cart")
async def view_cart_handler(callback_query: CallbackQuery, state: FSMContext):
    user = CustomUser.objects.filter(tg_id=callback_query.from_user.id).first()

    if not user:
        await callback_query.message.edit_text(
            text="📝 Botdan foydalanish uchun ro‘yxatdan o‘ting.\n\n"
                 "Iltimos, <b>ismingizni kiriting:</b> 👇"
        )
        await state.set_state(RegisterState.first_name)
        return

    orders = Cart.objects.filter(user_id=user.id).select_related('product')

    if not orders.exists():
        await callback_query.message.edit_text(
            "🛒 Sizning savatchingiz hozircha bo‘sh.",
            reply_markup=back_keyboard()
        )
        return

    text = "🛒 <b>Sizning savatchangizdagi mahsulotlar:</b>\n\n"
    total_price = 0

    for i, order in enumerate(orders, start=1):
        line_total = order.price * order.quantity
        total_price += line_total
        text += (
            f"🔸 <b>{i}. {order.product.name}</b>\n"
            f"   🔢 Miqdor: {order.quantity} ta\n"
            f"   💰 Narxi: {order.price:,} so‘m\n"
            f"   💵 Jami: {line_total:,} so‘m\n\n"
        )

    text += f"⭐ <b>Umumiy summa:</b> {total_price:,} so‘m"

    await callback_query.message.edit_text(text, reply_markup=cart_keyboard(user))




@dp.callback_query(F.data == "clear_cart")
async def clear_cart_handler(callback_query: CallbackQuery, state: FSMContext):
    user = CustomUser.objects.filter(tg_id=callback_query.from_user.id).first()

    if not user:
        await callback_query.message.edit_text(
            text="📝 Ro‘yxatdan o‘tishingiz kerak.\n"
                 "Iltimos, <b>ismingizni kiriting:</b> 👇"
        )
        await state.set_state(RegisterState.first_name)
        return

    Cart.objects.filter(user_id=user.id).delete()

    await callback_query.message.edit_text(
        "🧹 Savatcha muvaffaqiyatli tozalandi!",
        reply_markup=back_keyboard()
    )


@dp.callback_query(F.data == "view_profile")
async def view_profile_handler(callback_query: CallbackQuery, state: FSMContext):
    user = CustomUser.objects.filter(tg_id=callback_query.from_user.id).first()

    if not user:
        await callback_query.message.edit_text(
            "📝 Botdan foydalanish uchun ro‘yxatdan o‘ting.\n"
            "Iltimos, ismingizni kiriting: 👇"
        )
        await state.set_state(RegisterState.first_name)
        return

    text = (
        "👤 <b>Profil ma'lumotlari:</b>\n\n"
        f"🆔 Username: @{callback_query.from_user.username or 'Kiritilmagan'}\n"
        f"👨‍💼 Ism: {user.first_name or 'Kiritilmagan'}\n"
        f"👨‍👩‍👧 Familiya: {user.last_name or 'Kiritilmagan'}\n"
        f"📞 Telefon: {user.phone_number or 'Kiritilmagan'}\n"
    )

    await callback_query.message.edit_text(text, reply_markup=change_info_keyboard())




@dp.callback_query(F.data == "view_info")
async def view_info_handler(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "ℹ️ <b>Kerakli bo‘limni tanlang:</b> ⬇️",
        reply_markup=info_keyboard()
    )




@dp.callback_query(F.data == "change_profile_info")
async def change_profile_info_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(
        "✏️ <b>Yangi ismingizni kiriting:</b>"
    )
    await state.set_state(RegisterState.first_name)



@dp.callback_query(F.data == "leave_comment")
async def leave_comment_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("💬 <b>Izohingizni kiriting:</b>")
    await state.set_state(OrderState.leave_feedback)




@dp.callback_query(F.data == "delivery_terms")
async def delivery_terms_handler(callback_query: CallbackQuery):
    text = (
        "🚚 <b>Yetkazib berish shartlari:</b>\n\n"
        "1️⃣ Buyurtmalar 1–3 ish kuni ichida yetkazib beriladi.\n"
        "2️⃣ Narx manzilga qarab o‘zgaradi.\n"
        "3️⃣ Buyurtma tasdiqlangandan so‘ng bekor qilish imkoni mavjud emas.\n"
        "4️⃣ Qo‘shimcha savollar bo‘lsa, biz bilan bog‘laning."
    )

    await callback_query.message.edit_text(text, reply_markup=back_keyboard())


@dp.callback_query(F.data == "contacts")
async def contacts_handler(callback_query: CallbackQuery):
    text = (
        "☎️ <b>Aloqa ma'lumotlari:</b>\n\n"
        "📞 Telefon: +998 91 487 21 12\n"
        "📧 Email: eldorbekjuraev1993@gmail.com\n"
        "📍 Manzil: Andijon, Jaxon bozori\n"
        "🛍 O‘rikzor bozori — Gilam bozor / Samarbonu 39A/1"
    )

    await callback_query.message.edit_text(text, reply_markup=back_keyboard())
