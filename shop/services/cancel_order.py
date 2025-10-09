from shop.models import Order




def cancel_order(user_id, order_id):
    try:
        order = Order.objects.get(id=order_id, ordered_by=user_id,status="pending")
        order.status = "canceled"
        order.save()
        return True
    except Order.DoesNotExist:
        return False