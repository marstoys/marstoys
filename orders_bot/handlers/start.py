from aiogram import F
from aiogram.types import CallbackQuery,   Message
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.filters import Command , StateFilter
from orders_bot.models import  TelegramAdminsID
from orders_bot.dispatcher import dp,bot
from shop.models import Order, OrderItem,ImageProducts
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
    msg = await callback_query.message.edit_text(text="Iltimos, buyurtma raqamini kiriting:", reply_markup=back_keyboard())
    await state.update_data(msg=msg.message_id)
    await state.set_state(OrderState.waiting_for_order_number)

@dp.message(StateFilter(OrderState.waiting_for_order_number))
async def process_order_number(message: Message,state: FSMContext):
    order_number = message.text.strip()
    data = await state.get_data()
    await message.delete()
    msg_id = data.get("msg")
    if msg_id:
        del data["msg"]
        await state.update_data(data)
        try:
            await bot.delete_message(
                chat_id=message.chat.id,
                message_id=msg_id
            )
        except Exception:
            pass
    
    try:
        order = Order.objects.get(order_number=str(order_number))
        if order.status == 'cancelled':
            await message.answer(text="❌ Bu buyurtma bekor qilingan.",reply_markup=back_keyboard())
            await state.clear()
            return
        orderitems = OrderItem.objects.filter(order_id=order.id)

        if not orderitems.exists():
            await message.answer("❌ Bu buyurtmada mahsulotlar topilmadi.")
            return

        total_sum = sum(item.calculated_total_price for item in orderitems)

        details_text = (
            f"📦 <b>Buyurtma tafsilotlari</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 <b>Buyurtma raqami:</b> <code>{order.order_number}</code>\n"
            f"👤 <b>Ism:</b> {order.ordered_by.first_name}\n"
            f"📞 <b>Tel:</b> <code>{order.ordered_by.phone_number}</code>\n"
            f"🏠 <b>Manzil:</b> {order.ordered_by.address}\n"
            f"💳 <b>To‘lov usuli:</b> {order.payment_method.capitalize()}\n"
            f"💰 <b>To‘lov holati:</b> {'✅ To‘langan' if order.is_paid else '❌ To‘lanmagan'}\n"
            f"📦 <b>Buyurtma holati:</b> {order.get_status_display()}\n"
            f"🕒 <b>Sana:</b> {timezone.localtime(order.created_datetime).strftime('%Y-%m-%d %H:%M')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🧸 <b>Buyurtmadagi mahsulotlar:</b>\n\n"
        )

        media_group = MediaGroupBuilder()
        added_images = set()  

        for index, item in enumerate(orderitems, start=1):
            product = item.product
            images = product.images.filter(color=item.color).first()
            image_url = images.image.url if images else None

            details_text += (
                f"{index}. {product.name}\n"
                f"   📦 Soni: {item.quantity}\n"
                f"   🎨 Rangi: {item.get_color_display()}\n"
                f"   💰 Narxi: {item.calculated_total_price} UZS\n"
                f"   {f'📦 Karopka raqami: {product.manufacturer_code}\n' if product.manufacturer_code else ''}\n"
            )

            if image_url and image_url not in added_images:
                media_group.add_photo(media=image_url)
                added_images.add(image_url)

        details_text += f"\n━━━━━━━━━━━━━━━━━━━━━━━\n💰 <b>Jami to‘lov:</b> {total_sum} UZS"

        built_media = media_group.build()
        sent_message_ids = []
        if built_media:
            sent_messages = await message.answer_media_group(built_media)
            sent_message_ids = [m.message_id for m in sent_messages]


            await bot.send_message(
        chat_id=message.chat.id,
        text=details_text,
        parse_mode="HTML",
        reply_markup=change_order_status_keyboard(order.order_number),
        reply_to_message_id=sent_messages[0].message_id
    )

        else:
            await message.answer(
                details_text,
                parse_mode="HTML",
                reply_markup=change_order_status_keyboard(order.order_number)
            )
        await state.update_data(
            order_number=order.order_number,
            message_ids=sent_message_ids
        )
    except Order.DoesNotExist:
        await message.answer(
            text=(
                "❌ Kechirasiz, bunday buyurtma raqami topilmadi.\n"
                "Iltimos, qayta urinib ko‘ring yoki /start buyrug‘ini bosing."
            ),
            reply_markup=back_keyboard()
        )


@dp.callback_query(F.data == "back")
async def back_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(text="Assalomu alaykum. Bu bot sizga Buyurtmalarni avtomatik yuborib boradi.",reply_markup=main_keyboard())
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

@dp.callback_query(F.data.startswith("status_"))
async def order_status_handler(callback_query: CallbackQuery,state: FSMContext):
    new_status = callback_query.data.split("_")[1]
    order_number = callback_query.data.split("_")[-1]
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
    try:
        if new_status == 'cancelled':
            order = Order.objects.get(order_number=order_number,status="pending",is_paid=False)
            orderitems = OrderItem.objects.filter(order_id=order.id)
            for item in orderitems:
                image = ImageProducts.objects.filter(product_id=item.product.id,color=item.color).first()
                image.quantity += item.quantity
                image.save()
        else:
            order = Order.objects.get(order_number=order_number)
            order.status = new_status
            order.save()
        await callback_query.message.edit_text(text="Assalomu alaykum. Bu bot sizga Buyurtmalarni avtomatik yuborib boradi.",reply_markup=main_keyboard())
        await callback_query.answer(text=f"Buyurtma holati '{order.get_status_display()}' ga o'zgartirildi.", show_alert=True)
    except Order.DoesNotExist:
        await callback_query.answer(text="Buyurtma topilmadi.", show_alert=True)
    await state.clear()