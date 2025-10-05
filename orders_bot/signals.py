from django.utils import timezone
from orders_bot.models import TelegramAdminsID
from orders_bot.bot import bot
from orders_bot.buttons.inline import change_order_status_keyboard

def send_order_message(data):
    """
    Order yaratilib, transaction commit bo'lgandan keyin telegramga xabar yuboradi
    """
    msg = (
        f"🆕 Yangi buyurtma:\n\n"
        f"🆔 Buyurtma raqami: <code>{data.get('order_number')}</code>\n"
        f"👤 Ism: <b>{data.get('first_name')}</b>\n"
        f"📞 Tel: <code>{data.get('phone_number')}</code>\n"
        f"🏠 Manzil: {data.get('address')}\n"
        f"💳 To'lov usuli: {data.get('payment_method').capitalize()}\n"
        f"💳 To'langanligi : {"Tolangan" if bool(data.get('is_paid')) else "To'lanmagan" }\n"
        f"🕒 Sana: {timezone.localtime(data.get('created_datetime')).strftime('%Y-%m-%d %H:%M')}"
        f"\n\n📦 Buyurtma tafsilotlari:\n"
    )

    for index, item in enumerate(data.get('items', [])):
        msg += (
            f" {index + 1}. {item.get('product_name')} (x{item.get('quantity')}): {item.get('calculated_total_price')} \n Rangi - {item.get('color')}\n Karopka raqami - {item.get("manufacturer_code")}\n"
        )

    msg += f"\n💰 Jami to'lov: {sum(item.get('calculated_total_price') for item in data.get('items', []))} UZS"

    for tg_id in TelegramAdminsID.objects.all():
        if tg_id:
            try:
                bot.send_message(chat_id=tg_id.tg_id, text=msg)
                print(f"✅ Yuborildi: {tg_id.tg_id}")
            except Exception as e:
                print(f"❌ Yuborilmadi: {tg_id.tg_id}")
