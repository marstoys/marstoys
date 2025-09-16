from shop.models import  OrderItem,Order








def get_order_history(user_id,lang="uz"):
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
            "items": []
        }
        order_items=OrderItem.objects.filter(order_id=order.id)
        for item in order_items:
            order_dict["items"].append({
                "item_id": item.id,
                "product_id": item.product.id,
                "product_name": item.product.name if lang == "uz" else item.product.name_ru if lang == "ru" else item.product.name_en,
                "price": float(item.product.price),
                "quantity": item.quantity,
                "image": [img.image for img in item.product.images.all()]
            })

        result.append(order_dict)

    return result