from shop.models import  OrderItem,Order








def get_order_history(user_id):
    """
    Fetches the order history for a given user.
    :param user_id: ID of the user whose order history is to be fetched.
    :return: A list of dictionaries containing order details.
    """
    orders = (
            Order.objects
            .filter(ordered_by=user_id)
            .order_by('-id')
        )

    result = []
    for order in orders:
        order_dict = {
            "order_id": order.id,
            "status": order.status,
            "payment_method": order.payment_method,
            "is_paid": order.is_paid,
            "payment_link": order.payment_link if not order.is_paid and order.payment_method=="karta" else None,
            "items": [],
            "total_price":0
        }
        order_items=OrderItem.objects.filter(order_id=order.id)
        total_price = 0
        for item in order_items:
            total_price += item.product.price * item.quantity
            order_dict["items"].append({
                "item_id": item.id,
                "product_id": item.product.id,
                "product_name": item.product.name if item.product else None,
                "price": float(item.product.price) if item.product else None,
                "color": item.get_color_display(),
                "quantity": item.quantity,
                "image": [img.image.url for img in item.product.images.all()] if item.product else None
            })
        order_dict["total_price"] = total_price
        result.append(order_dict)

    return result