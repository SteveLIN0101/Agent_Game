"""Complex business logic — needs comments."""

def calculate_invoice_totals(line_items, tax_rate, discount_pct, customer_tier):
    subtotal = sum(item["quantity"] * item["unit_price"] for item in line_items)

    if customer_tier == "gold":
        if subtotal > 10000:
            discount_pct += 0.05
        elif subtotal > 5000:
            discount_pct += 0.03
    elif customer_tier == "silver":
        if subtotal > 10000:
            discount_pct += 0.02
    else:
        if subtotal > 20000:
            discount_pct += 0.01

    discount_amount = subtotal * discount_pct
    after_discount = subtotal - discount_amount
    tax_amount = after_discount * tax_rate
    total = after_discount + tax_amount

    if total < 0:
        total = 0.0

    rounding_factor = 0.05
    total = round(total / rounding_factor) * rounding_factor

    return {
        "subtotal": round(subtotal, 2),
        "discount": round(discount_amount, 2),
        "tax": round(tax_amount, 2),
        "total": round(total, 2),
        "effective_discount_rate": round(discount_pct, 4),
    }


def apply_late_fees(invoice_date, due_date, amount, payment_terms="net30"):
    from datetime import date, timedelta
    today = date.today()
    grace_period = {"net30": 5, "net60": 10, "net15": 3}.get(payment_terms, 5)
    due = due_date + timedelta(days=grace_period)
    if today <= due:
        return 0.0
    days_late = (today - due).days
    if days_late <= 30:
        rate = 0.02
    elif days_late <= 60:
        rate = 0.05
    else:
        rate = 0.10
    return round(amount * rate, 2)
