"""Tests for pricing module."""

import pytest
from src.pricing import calculate_total, apply_tax, calculate_shipping


class TestCalculateTotal:
    """Test discount calculation logic."""

    def test_no_coupons(self):
        """No coupons applied — price unchanged."""
        assert calculate_total(100) == 100.0
        assert calculate_total(50) == 50.0

    def test_percent_only(self):
        """Only percentage coupon."""
        assert calculate_total(100, percent_coupon=0.10) == 90.0
        assert calculate_total(200, percent_coupon=0.25) == 150.0

    def test_fixed_only(self):
        """Only fixed amount coupon."""
        assert calculate_total(100, fixed_coupon=15) == 85.0
        assert calculate_total(50, fixed_coupon=10) == 40.0

    def test_both_coupons(self):
        """Both percent and fixed coupons — percent applied first."""
        result = calculate_total(100, percent_coupon=0.10, fixed_coupon=15)
        # 100 * 0.9 - 15 = 75
        assert result == 75.0

    def test_zero_base_price(self):
        assert calculate_total(0, percent_coupon=0.10, fixed_coupon=5) == 0.0


class TestApplyTax:
    def test_standard_tax(self):
        assert apply_tax(100) == 108.0

    def test_zero_tax(self):
        assert apply_tax(100, tax_rate=0) == 100.0


class TestCalculateShipping:
    def test_single_item(self):
        assert calculate_shipping(1) == 5.99

    def test_multiple_items(self):
        assert calculate_shipping(3) == 5.99 + 2 * 2.99

    def test_no_items(self):
        assert calculate_shipping(0) == 0.0
