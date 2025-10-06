from shop.models import Cart
from core.exceptions.exception import CustomApiException
from core.exceptions.error_messages import ErrorCodes






def get_cart_product(user_id):
    cart_products=Cart.objects.filter(user_id=user_id).select_related("product__category").prefetch_related("product__images")
    if not cart_products.exists():
        raise CustomApiException(ErrorCodes.NOT_FOUND, message="The cart is empty.")
    data=[]
    for item in cart_products:
        data.append({
            "id": item.id,
            "name": item.product.name,
            "category": item.product.category.name if item.product.category else None,
            "price": item.product.price,
            "quantity": item.quantity,
            "discount": item.product.discount,
            "video_url": item.product.video_url,
            "discounted_price": item.product.discounted_price,
            "average_rating": item.product.average_rating,
            "description": item.product.description,
            "sold_count": item.product.sold,
            "images": [
                {
                    "id": image.id,
                    "image": image.image.url,
                    "color": image.color,
                    "quantity": image.quantity,
                } for image in item.product.images.all()
            ],
        })
    return data