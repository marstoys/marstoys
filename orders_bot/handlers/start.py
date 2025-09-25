from aiogram import F
from aiogram.types import CallbackQuery,   Message
from aiogram.filters import Command , StateFilter
from orders_bot.models import  TelegramAdminsID
from orders_bot.dispatcher import dp
from shop.models import Order, OrderItem
from orders_bot.buttons.inline import *
from aiogram.fsm.context import FSMContext
from orders_bot.state import OrderState
from django.utils import timezone

@dp.message(Command("start"))
async def start(message: Message) -> None:
    if not TelegramAdminsID.objects.filter(tg_id=message.from_user.id).exists():
        TelegramAdminsID.objects.create(tg_id=message.from_user.id)
    await message.answer(text="Assalomu alaykum. Bu bot sizga Buyurtmalarni avtomatik yuborib boradi.",reply_markup=main_keyboard())



@dp.callback_query(F.data == "check_order_number")
async def order_number_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(text="Iltimos, buyurtma raqamini kiriting:", reply_markup=back_keyboard())
    await state.set_state(OrderState.waiting_for_order_number)


@dp.message(StateFilter(OrderState.waiting_for_order_number))
async def process_order_number(message: Message, state: FSMContext):
    order_number = message.text.strip()
    try:
        order = Order.objects.get(order_number=str(order_number))
        msg = (
            f"📦 Buyurtma:\n\n"
            f"🆔 Buyurtma raqami: <code>{order.order_number}</code>\n"
            f"👤 Ism: <b>{order.ordered_by.first_name}</b>\n"
            f"📞 Tel: <code>{order.ordered_by.phone_number}</code>\n"
            f"🏠 Manzil: {order.ordered_by.address}\n"
            f"💳 To'lov usuli: {order.payment_method.capitalize()}\n"
            f"📦 Buyurtma holati: {order.status}\n"
            f"🕒 Sana: {timezone.localtime(order.created_datetime).strftime('%Y-%m-%d %H:%M')}"
            f"\n\n📦 Buyurtma tafsilotlari:\n"
        )
        orderitem = OrderItem.objects.filter(order_id=order.id)
        for index, item in enumerate(orderitem):
            msg += (
                f" {index + 1}. {item.product.name} (x{item.quantity}): {item.calculated_total_price}\n Rangi - {item.color}\n Karopka raqami - {item.product.manufacturer_code}"
            )
        msg += f"\n💰 Jami to'lov: {sum(item.calculated_total_price for item in orderitem)} UZS"
        await message.answer(text=msg, reply_markup=change_order_status_keyboard(order.order_number))
    except Order.DoesNotExist:
        await message.answer(text="Kechirasiz, bunday buyurtma raqami topilmadi. Iltimos, qayta urinib ko'ring yoki /start buyrug'ini bosing.", reply_markup=back_keyboard())



@dp.callback_query(F.data == "back")
async def back_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(text="Assalomu alaykum. Bu bot sizga Buyurtmalarni avtomatik yuborib boradi.",reply_markup=main_keyboard())
    await state.clear()

@dp.callback_query(F.data.startswith("status_"))
async def order_status_handler(callback_query: CallbackQuery):
    new_status = callback_query.data.split("_")[1]
    order_number = callback_query.data.split("_")[-1]
    try:
        order = Order.objects.get(order_number=order_number)
        order.status = new_status
        order.save()
        await callback_query.message.edit_text(text="Assalomu alaykum. Bu bot sizga Buyurtmalarni avtomatik yuborib boradi.",reply_markup=main_keyboard())
        await callback_query.answer(text=f"Buyurtma holati '{order.status}' ga o'zgartirildi.", show_alert=True)
    except Order.DoesNotExist:
        await callback_query.answer(text="Buyurtma topilmadi.", show_alert=True)