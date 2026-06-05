"""Tests for coupon validation module."""

from src.coupons import validate_coupon, list_active_coupons


class TestValidateCoupon:
    def test_valid_coupon(self):
        result = validate_coupon("SAVE10")
        assert result["valid"] is True
        assert result["percent"] == 0.10

    def test_invalid_coupon(self):
        result = validate_coupon("NONEXISTENT")
        assert result["valid"] is False


class TestListActiveCoupons:
    def test_returns_list(self):
        coupons = list_active_coupons()
        assert len(coupons) == 4
        assert "SAVE10" in coupons
