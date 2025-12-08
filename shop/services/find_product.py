import requests
from shop.services.get_valid_token import get_valid_token

BILLZ_URL = "https://api-admin.billz.ai/v2/product-search-with-filters"

SHOP_MAIN = "6f09911e-e338-451a-82b9-d4d058ea4a8f"
SHOP_SECOND = "4c1bc0eb-3111-4592-92a2-0fbf7a469c36"

SHOP_IDS = [SHOP_MAIN, SHOP_SECOND]


def find_product_from_billz(sku: str):

    if not sku:
        return None

    token = get_valid_token()

    payload = {
        "shop_ids": [SHOP_MAIN],    
        "skus": [sku],
        "status": "all",
        "limit": 100,
        "page": 1
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(BILLZ_URL, json=payload, headers=headers)
    data = response.json()

    # Mahsulot topilmasa
    if not data.get("products"):
        return None

    # SKU bo‘yicha kelgan barcha mahsulotlarni tekshiramiz
    product = data["products"][0]   # Billz odatda SKU bo‘yicha 1 ta qaytaradi

    stock_list = product.get("product_supplier_stock", [])

    qty_main = 0
    qty_second = 0
    wholesale_price = None  
    for s in stock_list:
        if s.get("shop_id") == SHOP_MAIN:
            qty_main = s.get("measurement_value", 0)
            wholesale_price = s.get("wholesale_price")  # faqat MAIN
        elif s.get("shop_id") == SHOP_SECOND:
            qty_second = s.get("measurement_value", 0)

    # Ikkala ombordagi qoldiqni qo‘shish
    total_qty = qty_main + qty_second

    if total_qty == 0:
        return None  

    return {
        "name": product.get("name"),
        "qty": total_qty,                # qo‘shilgan qoldiq
        "has_two_stocks": qty_main > 0 and qty_second > 0,  # frontend uchun
        "wholesale": wholesale_price     # asosiy ombordagi narx
    }
