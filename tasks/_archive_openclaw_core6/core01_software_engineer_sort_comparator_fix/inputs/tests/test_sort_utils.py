"""Tests for sort utilities."""
from datetime import date
from src.sort_utils import sort_by_date, sort_by_name


class TestSortByDate:
    def test_ascending_order(self):
        items = [
            {"name": "c", "date": date(2025, 3, 15)},
            {"name": "a", "date": date(2025, 1, 10)},
            {"name": "b", "date": date(2025, 2, 20)},
        ]
        result = sort_by_date(items, ascending=True)
        assert result[0]["name"] == "a"
        assert result[1]["name"] == "b"
        assert result[2]["name"] == "c"

    def test_descending_order(self):
        items = [
            {"name": "a", "date": date(2025, 1, 10)},
            {"name": "c", "date": date(2025, 3, 15)},
            {"name": "b", "date": date(2025, 2, 20)},
        ]
        result = sort_by_date(items, ascending=False)
        assert result[0]["date"] == date(2025, 3, 15)
        assert result[2]["date"] == date(2025, 1, 10)

    def test_same_date_preserves_input_order(self):
        items = [
            {"name": "x", "date": date(2025, 1, 1)},
            {"name": "y", "date": date(2025, 1, 1)},
        ]
        result = sort_by_date(items)
        assert result[0]["name"] == "x"


class TestSortByName:
    def test_ascending(self):
        items = [{"name": "z"}, {"name": "a"}, {"name": "m"}]
        result = sort_by_name(items)
        assert result[0]["name"] == "a"
        assert result[-1]["name"] == "z"
