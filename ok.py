import requests
url = "https://api-admin.billz.ai/v2/products"
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRfcGxhdGZvcm1faWQiOiI3ZDRhNGMzOC1kZDg0LTQ5MDItYjc0NC0wNDg4YjgwYTRjMDEiLCJjb21wYW55X2lkIjoiMzIyNjRmZWUtMDY0My00ZmQ2LWJlYWQtOTgxMzkwNGNmMzM4IiwiZGF0YSI6IiIsImV4cCI6MTc0NTM5ODA2NCwiaWF0IjoxNzQ0MTAyMDY0LCJpZCI6IjdkN2EwZWE1LWY5YTItNGI1Ny04NWRkLTUwMzlhNDQ4Mzg2YyIsInVzZXJfaWQiOiJiMTI4NTcxMC0wNDExLTQ4MTktYjgxNi0xMDcwYzgyYzZmMWEifQ.8_Q5MaZjI4-2nUDE6YsAjPmc9M4jcH-5su7rV3uMlp8",
}
response = requests.get(url, headers=headers)
# print(response.text)
def quantity_get():
    data = response.json()
    target_barcode = "2000000136059"
    filtered_products = [
        p for p in data.get("products", [])
        if p.get("barcode") == target_barcode
    ]
    for product in filtered_products:
        print(f"Topildi: {product['name']}")
        for shop in product.get("shop_measurement_values", []):
            print(f"{shop['shop_name']} do‘konida miqdor: {shop['active_measurement_value']}")

quantity_get()