"""Hidden edge-case tests for scheduler."""
from src.scheduler import schedule_tasks, get_worker_loads


class TestHiddenEdgeCases:
    def test_zero_tasks(self):
        result = schedule_tasks(0)
        assert result == []

    def test_large_n(self):
        result = schedule_tasks(1000)
        assert len(result) == 1000

    def test_loads_sum_matches(self):
        for n in [0, 1, 7, 13, 50]:
            loads = get_worker_loads(n)
            assert sum(loads.values()) == n
