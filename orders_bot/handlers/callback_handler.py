from aiogram import F
from aiogram.types import CallbackQuery
from orders_bot.state import OrderState
from orders_bot.utils import check_user_subscription
from orders_bot.dispatcher import dp,bot
from orders_bot.buttons.inline import *
from aiogram.fsm.context import FSMContext



@dp.callback_query(F.data == "back")
async def back_handler(callback_query: CallbackQuery, state: FSMContext):
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
    await callback.message.answer(text="✅ Botdan foydalanishingiz mumkin.", reply_markup=main_menu_keyboard())



@dp.callback_query(F.data == "view_cart")
async def view_cart_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(text="Savatcha bo'sh.", reply_markup=main_menu_keyboard())

