"""Hidden tests for data migration."""
from src.migrate import migrate_data


class TestHidden:
    def test_empty_users(self):
        result = migrate_data([], [{"id": 1, "amount": 10}])
        assert len(result) == 1  # order still appears

    def test_empty_orders(self):
        result = migrate_data([{"id": 1, "name": "A"}], [])
        assert len(result) == 1  # user still appears

    def test_empty_both(self):
        result = migrate_data([], [])
        assert result == []

    def test_no_duplicate_pairings(self):
        users = [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]
        orders = [{"id": 101, "amount": 50}, {"id": 102, "amount": 75}]
        result = migrate_data(users, orders)
        # Should not produce cartesian product for matched pairs
        assert len(result) <= 4  # At most 2 direct pairs + unmatched
