from shop.models import Cart, Products
from core.exceptions.exception import CustomApiException
from core.exceptions.error_messages import ErrorCodes


def create_cart_product(user_id, data):
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    color_display = data.get('color')

    if not product_id:
        raise CustomApiException(ErrorCodes.INVALID_INPUT, message="Product ID is required.")
    if quantity is None:
        raise CustomApiException(ErrorCodes.INVALID_INPUT, message="Quantity is required.")
    if not color_display:
        raise CustomApiException(ErrorCodes.INVALID_INPUT, message="Color is required.")

    color_field = Cart._meta.get_field('color')
    color_display_to_value = {display: value for value, display in color_field.choices}
    color_value = color_display_to_value.get(color_display, color_display)

    try:
        product = Products.objects.get(id=product_id)
    except Products.DoesNotExist:
        raise CustomApiException(ErrorCodes.NOT_FOUND, message="The specified product does not exist.")

    cart_product, created = Cart.objects.get_or_create(
        user_id=user_id,
        product_id=product.id,
        color=color_value,
        defaults={'quantity': max(quantity, 0)}  
    )

    if not created:
        new_quantity = cart_product.quantity + quantity

        if new_quantity <= 0:
            cart_product.delete()
            return True

        cart_product.quantity = new_quantity
        cart_product.save()

    return True
