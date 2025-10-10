from django.utils import timezone
from orders_bot.models import TelegramAdminsID
from orders_bot.bot import bot

def send_order_message(data):
    """
    Order yaratilib, transaction commit bo'lgandan keyin telegramga xabar yuboradi
    """
    msg = (
    f"🆕 <b>Yangi buyurtma!</b>\n\n"
    f"📦 <b>Buyurtma ma'lumotlari:</b>\n"
    f"━━━━━━━━━━━━━━━━━━━━━━━\n"
    f"🆔 <b>Raqam:</b> <code>{data.get('order_number')}</code>\n"
    f"👤 <b>Mijoz:</b> {data.get('first_name')}\n"
    f"📞 <b>Telefon:</b> <code>{data.get('phone_number')}</code>\n"
    f"🏠 <b>Manzil:</b> {data.get('address')}\n"
    f"💳 <b>To‘lov usuli:</b> {data.get('payment_method').capitalize()}\n"
    f"💰 <b>Holat:</b> {'✅ To‘langan' if bool(data.get('is_paid')) else '❌ To‘lanmagan'}\n"
    f"🕒 <b>Sana:</b> {timezone.localtime(data.get('created_datetime')).strftime('%Y-%m-%d %H:%M')}\n"
    f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    f"🧸 <b>Buyurtma tarkibi:</b>\n"
)

    # Har bir mahsulotni tartibli chiqarish
    for index, item in enumerate(data.get('items', []), start=1):
        msg += (
            f"\n<b>{index}. {item.get('product_name')}</b>\n"
            f"   🔢 Soni: {item.get('quantity')}\n"
            f"   🎨 Rangi: {item.get('color')}\n"
            f"   💰 Narxi: {item.get('calculated_total_price')} UZS\n"
            f"   {f'📦 Karopka raqami: {item.get('manufacturer_code')}\n' if item.get('manufacturer_code') else ''}"
        )

    # Jami summa
    total = sum(item.get('calculated_total_price') for item in data.get('items', []))
    msg += f"\n━━━━━━━━━━━━━━━━━━━━━━━\n💰 <b>Jami to‘lov:</b> {total} UZS"

    for tg_id in TelegramAdminsID.objects.all():
        if tg_id:
            try:
                bot.send_message(chat_id=tg_id.tg_id, text=msg)
                print(f"✅ Yuborildi: {tg_id.tg_id}")
            except Exception as e:
                print(f"❌ Yuborilmadi: {tg_id.tg_id}")


def send_order_cancellation_message(data):
    """
    Order bekor qilindi, transaction commit bo'lgandan keyin telegramga xabar yuboradi
    """
    msg = (
    f"❌ <b>Buyurtma bekor qilindi!</b>\n\n"
    f"📦 <b>Buyurtma ma'lumotlari:</b>\n"
    f"━━━━━━━━━━━━━━━━━━━━━━━\n"
    f"🆔 <b>Raqam:</b> <code>{data.get('order_number')}</code>\n"
    f"👤 <b>Mijoz:</b> {data.get('first_name')}\n"
    f"📞 <b>Telefon:</b> <code>{data.get('phone_number')}</code>\n"
    f"🏠 <b>Manzil:</b> {data.get('address')}\n"
    f"💳 <b>To‘lov usuli:</b> {data.get('payment_method').capitalize()}\n"
    f"🕒 <b>Sana:</b> {timezone.localtime(data.get('created_datetime')).strftime('%Y-%m-%d %H:%M')}\n"
    f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    f"🧸 <b>Buyurtma tarkibi:</b>\n"
    
)


    for index, item in enumerate(data.get('items', []), start=1):
        msg += (
            f"\n<b>{index}. {item.get('product_name')}</b>\n"
            f"   🔢 Soni: {item.get('quantity')}\n"
            f"   🎨 Rangi: {item.get('color')}\n"
            f"   💰 Narxi: {item.get('calculated_total_price')} UZS\n"
            f"   {f'📦 Karopka raqami: {item.get('manufacturer_code')}\n' if item.get('manufacturer_code') else ''}"
        )
    for tg_id in TelegramAdminsID.objects.all():
        if tg_id:
            try:
                bot.send_message(chat_id=tg_id.tg_id, text=msg)
                print(f"✅ Yuborildi: {tg_id.tg_id}")
            except Exception as e:
                print(f"❌ Yuborilmadi: {tg_id.tg_id}")