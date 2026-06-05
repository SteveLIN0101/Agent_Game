"""Tests for data migration."""
from src.migrate import migrate_data, count_migrated


class TestMigrateData:
    def test_equal_lengths(self):
        users = [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]
        orders = [{"id": 101, "amount": 50}, {"id": 102, "amount": 75}]
        result = migrate_data(users, orders)
        assert len(result) == 2

    def test_more_users_than_orders(self):
        """Users without orders should not be dropped."""
        users = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Charlie"},
        ]
        orders = [{"id": 101, "amount": 50.0}]
        result = migrate_data(users, orders)
        assert len(result) >= 3, f"Expected >= 3 rows, got {len(result)}"
        # All users should appear
        user_ids = {r["user_id"] for r in result}
        assert user_ids == {1, 2, 3}

    def test_more_orders_than_users(self):
        """Orders without users should not be dropped."""
        users = [{"id": 1, "name": "Alice"}]
        orders = [
            {"id": 101, "amount": 50.0},
            {"id": 102, "amount": 75.0},
        ]
        result = migrate_data(users, orders)
        assert len(result) >= 2, f"Expected >= 2 rows, got {len(result)}"


class TestCountMigrated:
    def test_all_preserved_flag(self):
        users = [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]
        orders = [{"id": 101, "amount": 50}]
        stats = count_migrated(users, orders)
        assert stats["all_preserved"] is True
