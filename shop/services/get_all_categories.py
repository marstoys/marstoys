from shop.models import Category




def get_all_categories():
    categories=Category.objects.all()
    date_info=[]
    for category in categories:
        category_data = {
            "id": category.id,
            "name": category.name,
            "product_count": category.product_count
        }
        date_info.append(category_data)
    return date_info