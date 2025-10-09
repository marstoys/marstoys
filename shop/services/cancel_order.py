from shop.models import Order,ImageProducts,OrderItem
from orders_bot.signals import send_order_cancellation_message



def cancel_order(user_id, order_id):
    try:
        order = Order.objects.get(id=order_id, ordered_by=user_id,status="pending",is_paid=False)
        order.status = "canceled"
        order.save()
        order_items = OrderItem.objects.filter(order_id=order.id)
        for item in order_items:
            image = ImageProducts.objects.filter(product_id=item.product.id,color=item.color).first()
            image.quantity += item.quantity
            image.save()
        data={
            "order_number": order.order_number,
            "first_name": order.ordered_by.full_name,
            "phone_number": order.ordered_by.phone_number,
            "address": order.ordered_by.address,
            "payment_method": order.payment_method,
            "created_datetime": order.created_datetime,
        }
        send_order_cancellation_message(data)
        
        return True
    except Order.DoesNotExist:
        return False