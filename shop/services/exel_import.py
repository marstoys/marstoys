import pandas as pd
from shop.models import Products,Category




def save_excel_to_db(excel_file):
    df = pd.read_excel(excel_file)

    for _, row in df.iterrows():
        category = Category.objects.filter(name=row.get("category")).first()
        Products.objects.create(
            category_id=category.id if category else None,
            name=row.get("product_name"),
            sku = row.get("sku"),
            price=row.get("price (so'm)"),
            quantity=row.get("quantity"),
           manufacturer_code =row.get("manufacturer_code"),
           discount=row.get("discount (foizda)"),
           description=row.get("description"),
           video_url=row.get("video_url"),
           
        )

    return len(df)  # nechta qator qo‘shilganini qaytaradi