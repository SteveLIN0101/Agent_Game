"""Tests for task registry."""

import pytest
from openclaw.task_registry import TaskRegistry, TaskRegistryError
from openclaw.models import TaskRole


class TestTaskRegistry:
    def test_loads_core01(self):
        reg = TaskRegistry()
        tasks = reg.list_tasks()
        assert len(tasks) >= 1
        task_ids = [t["id"] for t in tasks]
        assert "core01_software_engineer_discount_bug" in task_ids

    def test_get_existing_task(self):
        reg = TaskRegistry()
        task = reg.get("core01_software_engineer_discount_bug")
        assert task.role == TaskRole.SOFTWARE_ENGINEER
        assert task.difficulty.value == "medium"
        assert task.time_budget_minutes == 12

    def test_get_nonexistent_task(self):
        reg = TaskRegistry()
        with pytest.raises(TaskRegistryError, match="not found"):
            reg.get("nonexistent_task")

    def test_get_instructions(self):
        reg = TaskRegistry()
        task = reg.get("core01_software_engineer_discount_bug")
        inst = reg.get_instructions(task)
        assert len(inst) > 0
        assert "折扣" in inst or "Bug" in inst or "bug" in inst

    def test_list_input_files(self):
        reg = TaskRegistry()
        task = reg.get("core01_software_engineer_discount_bug")
        files = reg.list_input_files(task)
        assert "src/pricing.py" in files
        assert "tests/test_pricing.py" in files
        assert "issue.md" in files
        assert "CHANGELOG.md" in files

    def test_get_random(self):
        reg = TaskRegistry()
        task = reg.get_random()
        assert task.id is not None
        assert len(task.id) > 0

    def test_get_random_by_role(self):
        reg = TaskRegistry()
        task = reg.get_random(role="software_engineer")
        assert task.role == TaskRole.SOFTWARE_ENGINEER

    def test_get_random_nonexistent_role_raises(self):
        reg = TaskRegistry()
        # Filter by a role that doesn't exist in any task
        with pytest.raises(TaskRegistryError, match="Unknown role"):
            reg.get_random(role="nonexistent_role")
