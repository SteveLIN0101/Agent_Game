"""Order pricing module."""


def calculate_total(base_price: float, percent_coupon: float = 0.0,
                    fixed_coupon: float = 0.0) -> float:
    """Calculate final order total after coupons.

    Args:
        base_price: Original order price before discounts
        percent_coupon: Percentage discount as decimal (e.g. 0.10 = 10%)
        fixed_coupon: Fixed amount discount in dollars

    Returns:
        Final price after applying all discounts
    """
    # BUG: Should apply percent first, then fixed.
    # Current code subtracts fixed first, then applies percent.
    total = base_price - fixed_coupon
    total = total * (1 - percent_coupon)

    # BUG: Missing negative price clamp.
    # Should be: total = max(total, 0.0)

    return round(total, 2)


def apply_tax(price: float, tax_rate: float = 0.08) -> float:
    """Apply sales tax to a price."""
    return round(price * (1 + tax_rate), 2)


def calculate_shipping(item_count: int, base_rate: float = 5.99) -> float:
    """Calculate shipping cost based on item count."""
    if item_count <= 0:
        return 0.0
    return round(base_rate + (item_count - 1) * 2.99, 2)
