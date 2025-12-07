import requests

def geocode_address(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "MarsToysBot/1.0 (nsardorbek776@gmail.com)"  # majburiy!
    }

    response = requests.get(url, params=params, headers=headers)

    # JSON emas bo'lsa → xato qaytarish
    try:
        data = response.json()
    except Exception:
        print("❌ JSON emas, server javobi:", response.text)
        return None, None

    if data:
        return float(data[0]["lat"]), float(data[0]["lon"])

    return None, None


# Test
print(geocode_address("Toshkent City"))
