"""Tests for access control module."""
from src.access_control import can_access, list_accessible_resources


class TestCanAccess:
    def test_admin_without_read_should_access(self):
        """Admin should access any resource even without explicit read permission."""
        assert can_access("admin1", "dashboard", role="admin", permissions=[]) is True

    def test_admin_with_read_should_access(self):
        """Admin with read permission should access."""
        assert can_access("admin1", "dashboard", role="admin", permissions=["read"]) is True

    def test_user_with_read_should_access(self):
        """Regular user with read should access."""
        assert can_access("user1", "dashboard", role="user", permissions=["read"]) is True

    def test_user_without_read_denied(self):
        """Regular user without read should be denied."""
        assert can_access("user1", "dashboard", role="user", permissions=[]) is False

    def test_user_with_other_permission_denied(self):
        """Write permission without read should be denied."""
        assert can_access("user1", "dashboard", role="user", permissions=["write"]) is False


class TestListAccessible:
    def test_admin_sees_all(self):
        perms = {"a": [], "b": ["read"], "c": []}
        result = list_accessible_resources("admin1", "admin", perms)
        assert set(result) == {"a", "b", "c"}

    def test_user_sees_only_read(self):
        perms = {"a": ["read"], "b": ["write"], "c": ["read"]}
        result = list_accessible_resources("user1", "user", perms)
        assert set(result) == {"a", "c"}
