"""Coupon validation and management."""


def validate_coupon(code: str) -> dict:
    """Validate a coupon code and return its discount details.

    Returns dict with 'valid', 'percent', 'fixed', 'description'.
    """
    coupons = {
        "SAVE10": {"percent": 0.10, "fixed": 0, "description": "10% off"},
        "FLAT15": {"percent": 0, "fixed": 15, "description": "$15 off"},
        "BUNDLE": {"percent": 0.10, "fixed": 15, "description": "10% + $15 off"},
        "HALF": {"percent": 0.50, "fixed": 0, "description": "50% off"},
    }

    if code in coupons:
        return {"valid": True, **coupons[code]}
    return {"valid": False, "percent": 0, "fixed": 0, "description": "Invalid"}


def list_active_coupons() -> list[str]:
    """Return list of currently active coupon codes."""
    return ["SAVE10", "FLAT15", "BUNDLE", "HALF"]
