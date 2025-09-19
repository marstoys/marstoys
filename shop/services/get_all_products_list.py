from shop.models import Products




def get_all_products_list(category_id=None, lang="uz"):
    """
    Fetches all products, optionally filtered by category.
    """
    queryset = Products.objects.prefetch_related("images").select_related("category")
    
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    
    products_data=[]
    queryset = queryset.order_by('-created_datetime')
    for product in queryset:

        product_data = {
            "id": product.id,
            "name": product.name if lang == "uz" else product.name_ru if lang == "ru" else product.name_en,
            "category": product.category.name if lang == "uz" else product.category.name_ru if lang == "ru" else product.category.name_en,
            "price": product.price,
            "colors": [color.name for color in product.color.all()],
            "quantity": product.quantity,
            "discount": product.discount,
            "video_url": product.video_url,
            "discounted_price": product.discounted_price,
            "average_rating": product.average_rating,
            "description": product.description if lang == "uz" else product.description_ru if lang == "ru" else product.description_en,
            "images": [ image.image.url for image in product.images.all()],
            "sold_count": product.sold
        }
        products_data.append(product_data)

    return products_data
