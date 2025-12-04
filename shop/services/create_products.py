from shop.models import Products,Category,ImageProducts
from core.exceptions.error_messages import ErrorCodes
from core.exceptions.exception import CustomApiException

def create_products(data,images):
    category_id = data.get("category_id")
    product_name = data.get("product_name")
    price = data.get("price")
    discount = data.get("discount", 0)
    quantity = data.get("quantity", 0)
    description = data.get("description", "")
    sku = data.get("sku", "")
    video_url = data.get("video_url", "")
    
    
    category = Category.objects.filter(id=category_id).first() 
    if not category:
        raise CustomApiException(ErrorCodes.NOT_FOUND, "Category not found")
    
    product = Products.objects.create(
        category_id=category_id,
        name=product_name,
        price=price,
        discount=discount,
        quantity=quantity,
        description=description,
        sku=sku,
        video_url=video_url
    )
    for image in images:
        ImageProducts.objects.create(
            product_id=product.id,
            image=image
        )
    
    