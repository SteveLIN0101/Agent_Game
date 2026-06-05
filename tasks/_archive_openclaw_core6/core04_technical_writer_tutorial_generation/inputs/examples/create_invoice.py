"""Complete example: Create an invoice."""
import os, requests
API_KEY = os.getenv("API_KEY", "demo-key")
BASE_URL = "https://api.example.com/v2"

def create_invoice(customer_id, line_items, due_date=None, currency="USD"):
    payload = {"customer_id": customer_id, "line_items": line_items, "currency": currency}
    if due_date: payload["due_date"] = due_date
    resp = requests.post(f"{BASE_URL}/invoices", json=payload, headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"})
    return resp.json()

if __name__ == "__main__":
    inv = create_invoice("cust_001", [{"description": "Consulting", "quantity": 5, "unit_price": 150.00}], due_date="2025-12-31")
    print(inv)
