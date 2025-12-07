from aiogram import F
from django.utils import timezone
from users.models import CustomUser
from orders_bot.state import ChannelImageState, OrderState
from aiogram.filters import StateFilter
from orders_bot.dispatcher import dp, bot
from orders_bot.buttons.inline import *
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from shop.models import Order, OrderItem, Products
from aiogram.utils.media_group import MediaGroupBuilder
import html


@dp.message(StateFilter(OrderState.waiting_for_order_number))
async def process_order_number(message: Message, state: FSMContext):

    order_number = message.text.strip()
    data = await state.get_data()

    await message.delete()

    msg_id = data.get("msg")
    if msg_id:
        try:
            await bot.delete_message(
                chat_id=message.chat.id,
                message_id=msg_id
            )
        except:
            pass

    # BUYURTMA TEKSHIRISH
    try:
        order = Order.objects.get(order_number=str(order_number))

        if order.status == "cancelled":
            await message.answer(
                "❌ <b>Bu buyurtma bekor qilingan.</b>",
                reply_markup=back_keyboard(),
                parse_mode="HTML"
            )
            await state.clear()
            return

        orderitems = OrderItem.objects.filter(order_id=order.id).prefetch_related("product__images")

        if not orderitems.exists():
            await message.answer("❌ Bu buyurtmada hech qanday mahsulot mavjud emas.")
            return

        # Umumiy summa
        total_sum = sum(item.calculated_total_price for item in orderitems)

        # 🔥 BUYURTMA TAFSILOTLARI MATNI
        details_text = (
            f"📦 <b>Buyurtma tafsilotlari</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 <b>Raqam:</b> <code>{order.order_number}</code>\n"
            f"👤 <b>Mijoz:</b> {order.ordered_by.first_name}\n"
            f"📞 <b>Telefon:</b> <code>{order.ordered_by.phone_number}</code>\n"
            f"🏠 <b>Manzil:</b> {order.ordered_by.address}\n"
            f"💳 <b>To‘lov turi:</b> {order.payment_method.capitalize()}\n"
            f"💰 <b>To‘lov holati:</b> {'✅ To‘langan' if order.is_paid else '❌ To‘lanmagan'}\n"
            f"📦 <b>Buyurtma holati:</b> {order.get_status_display()}\n"
            f"📅 <b>Sana:</b> {timezone.localtime(order.created_datetime).strftime('%Y-%m-%d %H:%M')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🧸 <b>Mahsulotlar:</b>\n\n"
        )

        # MULTI MEDIA GROUP
        media_group = MediaGroupBuilder()
        added_images = set()

        for index, item in enumerate(orderitems, start=1):
            product = item.product
            image = product.images.first()

            details_text += (
                f"<b>{index}. {product.name}</b>\n"
                f"🔢 Soni: {item.quantity} ta\n"
                f"💰 Narxi: {item.calculated_total_price:,} so‘m\n"
                f"{'📦 SKU: ' + product.sku if product.sku else ''}\n\n"
            )

            if image and image.image.url not in added_images:
                media_group.add_photo(media=image.image.url)
                added_images.add(image.image.url)

        details_text += f"━━━━━━━━━━━━━━━━━━━━━━\n💵 <b>Jami to‘lov:</b> {total_sum:,} so‘m"

        built_media = media_group.build()
        sent_message_ids = []

        if built_media:
            sent_msgs = await message.answer_media_group(built_media)
            sent_message_ids = [m.message_id for m in sent_msgs]

            await bot.send_message(
                chat_id=message.chat.id,
                text=details_text,
                parse_mode="HTML",
                reply_markup=change_order_status_keyboard(order.order_number),
                reply_to_message_id=sent_msgs[0].message_id
            )
        else:
            await message.answer(
                details_text,
                parse_mode="HTML",
                reply_markup=change_order_status_keyboard(order.order_number)
            )

        await state.update_data(order_number=order.order_number, message_ids=sent_message_ids)

    except Order.DoesNotExist:
        await message.answer(
            text=(
                "❌ <b>Bu raqam bo‘yicha buyurtma topilmadi.</b>\n"
                "Iltimos, tekshirib qayta urining."
            ),
            reply_markup=back_keyboard(),
            parse_mode="HTML"
        )



@dp.callback_query(F.data.startswith("status_"))
async def order_status_handler(callback_query: CallbackQuery, state: FSMContext):

    new_status = callback_query.data.split("_")[1]
    order_number = callback_query.data.split("_")[-1]

    data = await state.get_data()
    message_ids = data.get("message_ids", [])

    # Rasmli bloklarni o‘chirish
    for msg_id in message_ids:
        try:
            await bot.delete_message(callback_query.message.chat.id, msg_id)
        except:
            pass

    # Buyurtma olish
    order = Order.objects.filter(order_number=order_number).first()
    if not order:
        await callback_query.answer("❌ Buyurtma topilmadi.", show_alert=True)
        await state.clear()
        return

    # Bekor qilish — faqat pending + to‘lanmagan
    if new_status == "cancelled":
        if not (order.status == "pending" and not order.is_paid):
            await callback_query.answer(
                "❌ Faqat *kutilayotgan* va *to‘lanmagan* buyurtmalar bekor qilinadi.",
                show_alert=True
            )
            await state.clear()
            return

        for item in OrderItem.objects.filter(order=order):
            product = Products.objects.filter(id=item.product.id).first()
            product.quantity += item.quantity
            product.save()

    # STATUSNI O‘ZGARTIRISH
    order.status = new_status
    order.save()

    await callback_query.answer(
        text=f"✔️ Buyurtma holati: <b>{order.get_status_display()}</b>",
        show_alert=True
    )

    await callback_query.message.edit_text(
        "📦 <b>Buyurtmalar paneli</b>\nQuyidagi bo‘limlardan foydalanishingiz mumkin:",
        reply_markup=admin_keyboard(),
        parse_mode="HTML"
    )

    await state.clear()



@dp.message(StateFilter(OrderState.leave_feedback))
async def leave_feedback_handler(message: Message, state: FSMContext):

    feedback_text = html.escape(message.text.strip())
    user = CustomUser.objects.filter(tg_id=message.from_user.id).first()

    await message.answer(
        "✅ <b>Fikringiz uchun katta rahmat!</b>\nSizning takliflaringiz biz uchun juda muhim! 💙",
        reply_markup=main_menu_keyboard(user),
        parse_mode="HTML"
    )

    # ADMINLARGA YUBORISH
    for admin in CustomUser.objects.filter(role="admin"):
        try:
            await bot.send_message(
                chat_id=admin.tg_id,
                text=(
                    "📝 <b>Yangi foydalanuvchi fikri!</b>\n\n"
                    f"{feedback_text}\n\n"
                    f"👤 Kimdan: <a href=\"tg://user?id={message.from_user.id}\">{message.from_user.full_name}</a>"
                ),
                parse_mode="HTML"
            )
        except Exception as e:
            print("Admin xabar yuborishda xato:", e)

    await state.clear()



@dp.callback_query(F.data == "send_image_to_channel")
async def send_image_to_channel_handler(callback_query: CallbackQuery,state: FSMContext):
    await callback_query.answer()
    await callback_query.message.answer(
        "📷 Iltimos, kanalingizga yuborishni istagan rasmni yuboring."
    )
    await state.set_state(ChannelImageState.waiting_for_channel_image)
    
@dp.message(StateFilter(ChannelImageState.waiting_for_channel_image))
async def process_channel_image(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("❌ Iltimos, rasm yuboring.")
        return

    photo = message.photo[-1]
    await state.update_data(channel_image=photo.file_id)
    await message.answer("✅ Rasm qabul qilindi, endi mahsulot linkini yuboring.")
    await state.set_state(ChannelImageState.waiting_for_product_link)
    
@dp.message(StateFilter(ChannelImageState.waiting_for_product_link))
async def process_product_link(message: Message, state: FSMContext):
    product_link = message.text.strip()
    data = await state.get_data()
    channel_image = data.get("channel_image")
    await state.update_data(product_link=product_link)
    await message.answer_photo(photo=channel_image,caption=f"📤 Rasm kanalga yuborilsinmi",reply_markup=sending_to_channel_keyboard(product_link))
    
    
@dp.callback_query(F.data == "send_image_to_channel_confirmation")
async def send_image_to_channel_confirmation(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    channel_image = data.get("channel_image")
    product_link = data.get("product_link")

    if not channel_image or not product_link:
        await callback_query.answer("❌ Ma'lumotlar yetarli emas.", show_alert=True)
        await state.clear()
        return

    channels = ChannelsToSubscribe.objects.all()
    for channel in channels:
        try:
            await bot.send_photo(
                chat_id=channel.link,
                photo=channel_image,
                reply_markup=sending(product_link)
            )
        except Exception as e:
            print(f"Kanalga rasm yuborishda xato ({channel.link}):", e)

    await callback_query.message.answer("✅ Rasm muvaffaqiyatli yuborildi.",reply_markup=admin_keyboard())
    await state.clear()

@dp.callback_query(F.data == "cancel_sending_to_channel")
async def cancel_sending_to_channel(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("❌ Rasm yuborish bekor qilindi.",reply_markup=admin_keyboard())
    await state.clear()