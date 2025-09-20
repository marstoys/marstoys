from django.utils import timezone
from shop.models import Order,OrderItem
from orders_bot.models import TelegramAdminsID
from django.db.models.signals import post_save
from django.dispatch import receiver
from orders_bot.bot import bot



@receiver(post_save, sender=Order)
def order_created_handler(sender, instance, created, **kwargs):
    if created:
        msg = (
            f"🆕 Yangi zayafka:\n\n"
            f"🆔 Buyurtma raqami: {instance.order_number}\n"
            f"👤 Ism: {instance.ordered_by.first_name}\n"
            f"📞 Tel: {instance.ordered_by.phone_number}\n"
            f"🕒 Sana: {timezone.localtime(instance.created_datetime).strftime('%Y-%m-%d %H:%M')}"
            f"\n\n📦 Buyurtma tafsilotlari:\n"
        )
        orderitem = OrderItem.objects.filter(order_id=instance.id)
        for item in orderitem:
            msg += (
                f" - {item.product.name} (x{item.quantity}): {item.calculated_total_price} - {item.color}\n"
            )
        msg += f"\n💰 Jami to'lov: {sum(item.calculated_total_price for item in orderitem)} UZS"

        for tg_id in TelegramAdminsID.objects.all():
            if tg_id:
                result = bot.send_message(chat_id=tg_id.tg_id, text=msg)
                if result:
                    print(f"✅ Yuborildi: {tg_id.tg_id}")
                else:
                    print(f"❌ Xatolik: {tg_id.tg_id}")

