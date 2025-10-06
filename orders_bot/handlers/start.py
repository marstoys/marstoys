from aiogram import F
from aiogram.types import CallbackQuery,   Message,InputMediaPhoto
from aiogram.utils.media_group import MediaGroupBuilder
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
async def process_order_number(message: Message):
    order_number = message.text.strip()

    try:
        order = Order.objects.get(order_number=str(order_number))
        orderitems = OrderItem.objects.filter(order_id=order.id)

        if not orderitems.exists():
            await message.answer("❌ Bu buyurtmada mahsulotlar topilmadi.")
            return

        total_sum = sum(item.calculated_total_price for item in orderitems)

        details_text = (
            f"📦 <b>Buyurtma tafsilotlari</b>\n\n"
            f"🆔 <b>Buyurtma raqami:</b> <code>{order.order_number}</code>\n"
            f"👤 <b>Ism:</b> {order.ordered_by.first_name}\n"
            f"📞 <b>Tel:</b> <code>{order.ordered_by.phone_number}</code>\n"
            f"🏠 <b>Manzil:</b> {order.ordered_by.address}\n"
            f"💳 <b>To‘lov usuli:</b> {order.payment_method.capitalize()}\n"
            f"💰 <b>To‘lov holati:</b> {'✅ To‘langan' if order.is_paid else '❌ To‘lanmagan'}\n"
            f"📦 <b>Buyurtma holati:</b> {order.get_status_display()}\n"
            f"🕒 <b>Sana:</b> {timezone.localtime(order.created_datetime).strftime('%Y-%m-%d %H:%M')}\n\n"
            f"🧸 <b>Buyurtmadagi mahsulotlar:</b>\n\n"
        )

        # 🖼️ Media group yaratamiz
        media_group = MediaGroupBuilder()
        added_images = set()  

        for index, item in enumerate(orderitems, start=1):
            product = item.product
            image = product.images.first()
            image_url = image.image.url if image else None

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

        details_text += f"\n💰 <b>Jami to‘lov:</b> {total_sum} UZS"

        # 📸 Agar kamida 1 ta rasm bo‘lsa:
        built_media = media_group.build()
        if built_media:
            # barcha rasmlarni caption-siz yuboramiz
            sent_messages = await message.answer_media_group(built_media)

            # oxirgi yuborilgan xabarni olamiz
            last_message = sent_messages[-1]

            # so‘ng shu postga javoban tafsilotlarni tugma bilan yuboramiz
            await message.reply(
                details_text,
                parse_mode="HTML",
                reply_markup=change_order_status_keyboard(order.order_number),
                reply_to_message_id=last_message.message_id
            )

        else:
            # agar rasm bo‘lmasa — faqat matn yuboriladi
            await message.answer(
                details_text,
                parse_mode="HTML",
                reply_markup=change_order_status_keyboard(order.order_number)
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
        await callback_query.answer(text=f"Buyurtma holati '{order.get_status_display()}' ga o'zgartirildi.", show_alert=True)
    except Order.DoesNotExist:
        await callback_query.answer(text="Buyurtma topilmadi.", show_alert=True)