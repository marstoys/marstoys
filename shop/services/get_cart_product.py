from shop.models import Cart,ProductColor
from core.exceptions.exception import CustomApiException
from core.exceptions.error_messages import ErrorCodes






def get_cart_product(user_id):
    cart_products=Cart.objects.filter(user_id=user_id).select_related("product__category").prefetch_related("product__colors__images")
    if not cart_products.exists():
        raise CustomApiException(ErrorCodes.NOT_FOUND, message="The cart is empty.")
    data=[]
    for item in cart_products:
        product_color = ProductColor.objects.filter(product_id=item.product.id,color=item.color).first()
        data.append({
            "id": item.id,
            "product_id": item.product.id,
            "name": item.product.name,
            "category": item.product.category.name if item.product.category else None,
            "price": item.price,
            "quantity": item.quantity,
            "sklad_quantity": product_color.quantity if product_color else 0,
            "discount": item.product.discount,
            "video_url": item.product.video_url,
            "discounted_price": item.product.discounted_price,
            "average_rating": item.product.average_rating,
            "description": item.product.description,
            "sold_count": item.product.sold,
            "color": item.get_color_display(),
            "images": [img.make_https for img in product_color.images.all()] if product_color else [],
            
        })
    return data