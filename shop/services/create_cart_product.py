from shop.models import Cart, Products
from core.exceptions.exception import CustomApiException
from core.exceptions.error_messages import ErrorCodes





def create_cart_product(user_id,data):
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    color = data.get('color', 'white')

    if not product_id:
        raise CustomApiException(ErrorCodes.INVALID_INPUT, message="Product ID is required.")
        
    try:
        product = Products.objects.get(id=product_id)
    except Products.DoesNotExist:
        raise CustomApiException(ErrorCodes.NOT_FOUND, message="The specified product does not exist.")

    cart_product, created = Cart.objects.get_or_create(
        user_id=user_id,
        product=product,
        color=color,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_product.quantity += quantity
        cart_product.save()

    return True