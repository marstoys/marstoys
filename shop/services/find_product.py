import requests
from shop.services.get_valid_token import get_valid_token

BILLZ_URL = "https://api-admin.billz.ai/v2/product-search-with-filters"
SHOP_ID = "6f09911e-e338-451a-82b9-d4d058ea4a8f" 


def find_product_from_billz(sku: str):
    

    if not sku:
        return None

    token = get_valid_token()

    payload = {
        "shop_ids": [SHOP_ID],
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

    # Shu SHOP_ID bo‘yicha stock bor mahsulotni qidiramiz
    product = None
    for p in data["products"]:
        if any(s.get("shop_id") == SHOP_ID for s in p.get("product_supplier_stock", [])):
            product = p
            break

    if not product:
        return None

    stock = next(
        (s for s in product["product_supplier_stock"] if s.get("shop_id") == SHOP_ID),
        None
    )

    if not stock:
        return None

    return {
        "name": product.get("name"),
        "qty": stock.get("measurement_value"),
        "wholesale": stock.get("wholesale_price")
    }
