"""Task discovery and loading from the filesystem."""

import os
from pathlib import Path

import yaml

from .models import TaskConfig, TaskRole, Difficulty
from .config import TASKS_DIR


class TaskRegistryError(Exception):
    """Raised when task loading fails."""
    pass


class TaskRegistry:
    """Discovers and loads task instances from the tasks/ directory."""

    def __init__(self, tasks_dir: Path | None = None):
        self.tasks_dir = tasks_dir or TASKS_DIR
        self._tasks: dict[str, TaskConfig] = {}
        self._load_all()

    def _load_all(self) -> None:
        """Scan tasks_dir for subdirectories containing task.yaml."""
        if not self.tasks_dir.exists():
            return

        for entry in sorted(self.tasks_dir.iterdir()):
            if not entry.is_dir():
                continue
            task_yaml = entry / "task.yaml"
            if not task_yaml.exists():
                continue
            try:
                task = self._load_task(entry, task_yaml)
                self._tasks[task.id] = task
            except Exception as e:
                # Log warning but continue loading other tasks
                print(f"Warning: failed to load task from {entry}: {e}")

    def _load_task(self, task_dir: Path, yaml_path: Path) -> TaskConfig:
        """Parse a single task.yaml into a TaskConfig."""
        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        if not data or "id" not in data:
            raise TaskRegistryError(f"Invalid task.yaml in {task_dir}: missing 'id'")

        config = TaskConfig(
            id=data["id"],
            role=TaskRole(data["role"]),
            difficulty=Difficulty(data.get("difficulty", "medium")),
            time_budget_minutes=data.get("time_budget_minutes", 12),
            allowed_tools=data.get("allowed_tools", []),
            required_outputs=data.get("required_outputs", []),
            forbidden_actions=data.get("forbidden_actions", []),
            scoring=data.get("scoring", {}),
            task_dir=str(task_dir),
        )
        return config

    def get(self, task_id: str) -> TaskConfig:
        """Get a task by ID."""
        if task_id not in self._tasks:
            available = ", ".join(self._tasks.keys())
            raise TaskRegistryError(
                f"Task '{task_id}' not found. Available: {available}"
            )
        return self._tasks[task_id]

    def list_tasks(self) -> list[dict]:
        """List all available tasks with metadata."""
        return [
            {
                "id": t.id,
                "role": t.role.value,
                "difficulty": t.difficulty.value,
                "time_budget_minutes": t.time_budget_minutes,
            }
            for t in self._tasks.values()
        ]

    def get_random(self, role: str | None = None) -> TaskConfig:
        """Get a random task, optionally filtered by role."""
        import random
        candidates = list(self._tasks.values())
        if role:
            try:
                role_enum = TaskRole(role)
            except ValueError:
                raise TaskRegistryError(
                    f"Unknown role '{role}'. "
                    f"Valid roles: {', '.join(r.value for r in TaskRole)}"
                )
            candidates = [t for t in candidates if t.role == role_enum]
        if not candidates:
            raise TaskRegistryError("No tasks available")
        return random.choice(candidates)

    def get_instructions(self, task: TaskConfig) -> str:
        """Read the instructions.md for a task."""
        instructions_path = Path(task.task_dir) / "instructions.md"
        if not instructions_path.exists():
            raise TaskRegistryError(
                f"No instructions.md found for task {task.id}"
            )
        with open(instructions_path) as f:
            return f.read()

    def list_input_files(self, task: TaskConfig) -> list[str]:
        """List all files in the task's inputs directory."""
        inputs_dir = Path(task.task_dir) / "inputs"
        if not inputs_dir.exists():
            return []
        files = []
        for f in inputs_dir.rglob("*"):
            if f.is_file():
                rel = str(f.relative_to(inputs_dir))
                files.append(rel)
        return sorted(files)

    def __len__(self) -> int:
        return len(self._tasks)
