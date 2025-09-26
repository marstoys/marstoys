from shop.models import Products




def get_all_products_list(category_id=None):
    """
    Fetches all products, optionally filtered by category.
    """
    queryset = Products.objects.prefetch_related("images").select_related("category")
    
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    
    products_data = []
    queryset = queryset.order_by('-created_datetime')
    for product in queryset:
        product_data = {
            "id": product.id,
            "name": product.name ,
            "category": product.category.name if product.category else None,
            "price": product.price,
            "quantity": product.quantity,
            "discount": product.discount,
            "video_url": product.video_url,
            "discounted_price": product.discounted_price,
            "average_rating": product.average_rating,
            "description": product.description ,
            "sold_count": product.sold,
            "images": [
                {
                    "id": image.id,
                    "image": image.image.url,
                    "color": image.color
                } for image in product.images.all()
            ],
        }        
        products_data.append(product_data)

    return products_data
