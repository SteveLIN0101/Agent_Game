"""Example: Create an invoice via API v2."""

import requests

API_KEY = "your-api-key-here"
BASE_URL = "https://api.example.com/v2"

# BUG: missing colon after function definition
def create_invoice(customer_id, items)
    # BUG: variable name typo (line_items vs items)
    # BUG: wrong endpoint path (/v1 instead of /v2)
    url = f"{BASE_URL}/v1/invoices"

    # BUG: using deprecated 'user' parameter
    payload = {
        "user": customer_id,
        "items_text": str(items),
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}"
        # BUG: missing comma? No, but missing Content-Type
    }

    # BUG: requests typo
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Test
if __name__ == "__main__":
    result = create_invoice("cust_123", [{"description": "Widget", "quantity": 2, "unit_price": 9.99}])
    print(result)
