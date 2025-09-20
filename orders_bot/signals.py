from django.utils import timezone
from shop.models import OrderItem
from orders_bot.models import TelegramAdminsID
from orders_bot.bot import bot


def send_order_message(data):
    """
    Order yaratilib, transaction commit bo'lgandan keyin telegramga xabar yuboradi
    """
    msg = (
        f"🆕 Yangi buyurtma:\n\n"
        f"🆔 Buyurtma raqami: <code>{data.get('order_number')}</code>\n"
        f"👤 Ism: <code>{data.get('first_name')}</code>\n"
        f"📞 Tel: <code>{data.get('phone_number')}</code>\n"
        f"🕒 Sana: {timezone.localtime(data.get('created_datetime')).strftime('%Y-%m-%d %H:%M')}"
        f"\n\n📦 Buyurtma tafsilotlari:\n"
    )

    for item in data.get('items', []):
        msg += (
            f" - {item.get('product_name')} (x{item.get('quantity')}): {item.get('calculated_total_price')} - {item.get('color')}\n"
        )

    msg += f"\n💰 Jami to'lov: {sum(item.get('calculated_total_price') for item in data.get('items', []))} UZS"

    for tg_id in TelegramAdminsID.objects.all():
        if tg_id:
            try:
                bot.send_message(chat_id=tg_id.tg_id, text=msg)
                print(f"✅ Yuborildi: {tg_id.tg_id}")
            except Exception as e:
                print(f"❌ Yuborilmadi: {tg_id.tg_id}")
