from shop.models import Category




def get_all_categories(lang="uz", gender="all"):
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
            "name": category.name if lang == "uz" else category.name_ru if lang == "ru" else category.name_en,
            "product_count": category.product_count
        }
        date_info.append(category_data)
    return date_info