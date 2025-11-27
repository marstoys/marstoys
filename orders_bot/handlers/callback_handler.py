from aiogram import F
from aiogram.types import CallbackQuery
from orders_bot.state import OrderState
from orders_bot.utils import check_user_subscription
from orders_bot.dispatcher import dp,bot
from orders_bot.buttons.inline import *
from aiogram.fsm.context import FSMContext
from orders_bot.state import RegisterState
from users.models import CustomUser
from shop.models import Cart


@dp.callback_query(F.data == "back")
async def back_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    user = CustomUser.objects.filter(tg_id=callback_query.from_user.id).first()
    if user and user.role == "user":
        await callback_query.message.edit_text(text="Asosiy menu",reply_markup=main_menu_keyboard())
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
async def check_subscription(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await callback.answer()
    await callback.message.edit_text(text="🔄 Obunalar tekshirilmoqda...",reply_markup=None)
    subscription_results = await check_user_subscription(user_id)
    if not subscription_results:
        text = "❌ Iltimos, barcha kanallarga obuna bo'ling va tekshirish tugmasini bosing."
        await callback.message.edit_text(text=text, reply_markup=join_channels())
        return
    await callback.message.edit_text(text="✅ Botdan foydalanishingiz mumkin.", reply_markup=main_menu_keyboard())



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
    await callback_query.message.edit_text(text, reply_markup=back_keyboard())
        
