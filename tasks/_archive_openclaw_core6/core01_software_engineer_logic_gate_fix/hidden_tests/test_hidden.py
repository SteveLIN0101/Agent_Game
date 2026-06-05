"""Hidden edge-case tests for access control."""
from src.access_control import can_access


class TestHidden:
    def test_none_permissions(self):
        """None permissions should default to empty list."""
        result = can_access("user1", "x", role="user", permissions=None)
        assert result is False

    def test_admin_empty_string_resource(self):
        assert can_access("admin1", "", role="admin", permissions=[]) is True

    def test_case_sensitive_role(self):
        """Admin role check is case sensitive."""
        assert can_access("user1", "x", role="Admin", permissions=["read"]) is False
