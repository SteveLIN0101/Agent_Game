"""Hidden tests — agent cannot see these.

These are at /opt/verifier/hidden_tests/ in the container,
NOT in the workspace /workspace/.
"""

from src.pricing import calculate_total


def test_percent_then_fixed_coupon():
    """Percent applied first, then fixed."""
    assert calculate_total(100, percent_coupon=0.10, fixed_coupon=15) == 75.0


def test_total_never_negative():
    """Discounts cannot make total negative."""
    result = calculate_total(20, percent_coupon=0.50, fixed_coupon=15)
    assert result >= 0


def test_edge_case_exact_zero():
    """Discounts exactly equal base price."""
    result = calculate_total(50, percent_coupon=0, fixed_coupon=50)
    assert result == 0.0


def test_no_side_effect_on_other_functions():
    """apply_tax and calculate_shipping should still work."""
    from src.pricing import apply_tax, calculate_shipping

    assert apply_tax(100) == 108.0
    assert calculate_shipping(1) == 5.99
    assert calculate_shipping(0) == 0.0
