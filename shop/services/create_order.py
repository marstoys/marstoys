from core.constants import click_up
from decimal import Decimal
from shop.models import Order,OrderItem,Products
from users.models import CustomUser as User
from core.exceptions.error_messages import ErrorCodes
from core.exceptions.exception import CustomApiException






def create_order(data,user_id):
    user= User.objects.filter(id=user_id).first()
    if not user:
        raise CustomApiException(ErrorCodes.NOT_FOUND, "User not found")
    product_items=data.get('product_items')
    payment_method=data.get('payment_method', 'naxt')
    if not product_items:
        raise CustomApiException(ErrorCodes.NOT_FOUND, "Product items are required")
    order= Order.objects.create(
        ordered_by=user,
        payment_method=payment_method,
    )
    total_price = 0
    for item in product_items:
        product_id = item.get('product_id')
        quantity = item.get('quantity', 1)
        color = item.get('color')
        product=Products.objects.filter(id=product_id).first()
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            color=color
        )
        total_price += product.discounted_price * Decimal(str(quantity))
    if payment_method == "karta":
            payment_link = click_up.initializer.generate_pay_link(
                id=order.id,
                amount=total_price,
                return_url="https://toysmars.uz"
            )
            return payment_link
    return None