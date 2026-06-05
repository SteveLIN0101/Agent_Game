"""Tests for task scheduler."""
from src.scheduler import schedule_tasks, get_worker_loads


class TestScheduleTasks:
    def test_schedules_correct_count(self):
        for n in [1, 5, 10, 100]:
            result = schedule_tasks(n)
            assert len(result) == n, f"Expected {n} tasks, got {len(result)}"

    def test_round_robin_distribution(self):
        result = schedule_tasks(8)
        # 4 workers, 8 tasks: each worker gets 2
        assert result[0] == 0
        assert result[1] == 1
        assert result[2] == 2
        assert result[3] == 3
        assert result[4] == 0
        assert result[5] == 1
        assert result[6] == 2
        assert result[7] == 3

    def test_single_task(self):
        result = schedule_tasks(1)
        assert result == [0]


class TestGetWorkerLoads:
    def test_even_distribution(self):
        loads = get_worker_loads(12)
        for w in range(4):
            assert loads[w] == 3

    def test_uneven_distribution(self):
        loads = get_worker_loads(5)
        total = sum(loads.values())
        assert total == 5
