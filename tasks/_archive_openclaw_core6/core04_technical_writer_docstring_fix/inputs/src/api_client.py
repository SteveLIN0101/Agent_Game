"""API client for invoice management."""

import requests


class InvoiceClient:
    def __init__(self, api_key: str, base_url: str = "https://api.example.com/v2"):
        self.api_key = api_key
        self.base_url = base_url

    # BUG: Missing docstring
    def create_invoice(self, customer_id, line_items, due_date=None, currency="USD"):
        payload = {"customer_id": customer_id, "line_items": line_items, "currency": currency}
        if due_date:
            payload["due_date"] = due_date
        return requests.post(f"{self.base_url}/invoices", json=payload, headers={"Authorization": f"Bearer {self.api_key}"})

    # BUG: Missing docstring
    def list_invoices(self, customer_id=None, status=None):
        params = {}
        if customer_id: params["customer_id"] = customer_id
        if status: params["status"] = status
        return requests.get(f"{self.base_url}/invoices", params=params, headers={"Authorization": f"Bearer {self.api_key}"})

    # BUG: Missing docstring
    def get_invoice(self, invoice_id):
        return requests.get(f"{self.base_url}/invoices/{invoice_id}", headers={"Authorization": f"Bearer {self.api_key}"})
