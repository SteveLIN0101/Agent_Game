"""Every one of the 60 Red Dust tasks is runnable + auto-scored with a deep
grader (58 shared family graders + 2 bespoke graders), and each grader
discriminates a gold run from a bad one."""
from pathlib import Path

import pytest

from openclaw.reddust.engine import run_task_dir

TASKS = Path(__file__).resolve().parents[1] / "tasks"
TASK_DIRS = sorted(str(p) for p in TASKS.glob("rd_*") if (p / "task.yaml").exists())


def test_all_60_tasks_present():
    assert len(TASK_DIRS) == 60


def test_no_generic_scaffold_remains():
    generic = [Path(t).name for t in TASK_DIRS
               if "build_generic_tools" in (Path(t) / "tools.py").read_text(encoding="utf-8")]
    assert generic == []


@pytest.mark.parametrize("task_dir", TASK_DIRS,
                         ids=[Path(t).name for t in TASK_DIRS])
def test_gold_passes_and_beats_bad(task_dir):
    g = run_task_dir(task_dir, "gold")
    b = run_task_dir(task_dir, "bad")
    assert g["score"] >= 85, (task_dir, g["failure_reasons"])
    assert g["score"] - b["score"] >= 30, (task_dir, g["score"], b["score"])
