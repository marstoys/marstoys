from shop.models import Cart


def delete_grouped_cart_products(user_id, datas):
    color_field = Cart._meta.get_field('color')
    color_display_to_value = {display: value for value, display in color_field.choices}
    for item in datas:
        product_id = item.get("product_id")
        color_display = item.get("color")
        color_value = color_display_to_value.get(color_display, color_display)
        if not product_id or not color_value:
            continue

        Cart.objects.filter(
            user_id=user_id,
            product_id=product_id,
            color=color_value
        ).delete()

        
    return True
