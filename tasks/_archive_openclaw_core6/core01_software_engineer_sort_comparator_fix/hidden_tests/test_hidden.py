"""Hidden tests for sort comparator."""
from datetime import date
from src.sort_utils import sort_by_date


class TestHidden:
    def test_empty_list(self):
        assert sort_by_date([]) == []

    def test_single_item(self):
        items = [{"name": "x", "date": date(2025, 6, 15)}]
        assert sort_by_date(items) == items

    def test_many_items_ascending(self):
        items = [{"date": date(2025, i, 1)} for i in range(12, 0, -1)]
        result = sort_by_date(items, ascending=True)
        for i in range(11):
            assert result[i]["date"] <= result[i+1]["date"]
