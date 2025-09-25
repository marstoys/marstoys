from shop.models import Category




def get_all_categories( gender="all"):
    categories=Category.objects.all()
    if gender != "all":
        if gender == "male":
            categories=categories.exclude(gender="female")
        elif gender == "female":
            categories=categories.exclude(gender="male")
    date_info=[]
    for category in categories:
        category_data = {
            "id": category.id,
            "name": category.name ,
            "product_count": category.product_count
        }
        date_info.append(category_data)
    return date_info