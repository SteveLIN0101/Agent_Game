"""Run a Red Dust solution against a task and grade the resulting world.

Two layers:

* :func:`run_solution` — pure core: seed a World, let a ``solve`` callback drive
  the tools, then grade with ``verify``.  Trivially unit-testable.
* :func:`run_task_dir` — load ``task.yaml`` + ``inputs/`` + ``tools.py`` +
  ``verifier/verify.py`` + ``solutions/<name>.py`` from a task directory on
  disk and run them through :func:`run_solution`.
"""

import importlib.util
import json
from pathlib import Path
from typing import Any, Callable

import yaml

from .scoring import score_checks
from .world import World


def _result_card(spec: dict, result: dict) -> dict:
    card = dict(spec.get("visible_result_card") or {"title": spec.get("id", "")})
    card.setdefault("title", spec.get("id", ""))
    card["failure_reasons"] = result["failure_reasons"]
    return card


def run_solution(spec: dict, inputs: dict, build_tools: Callable,
                 solve: Callable, verify: Callable) -> dict:
    """Seed a World from the task's visible_state + inputs, run the solution's
    tool calls, then grade.  Returns score + result card + replay trajectory."""
    world = World(state=spec.get("visible_state", {}), inputs=inputs)
    tools = build_tools(world)
    solve(tools, world)
    checks = verify(world)
    result = score_checks(checks)
    result["task_id"] = spec.get("id")
    result["result_card"] = _result_card(spec, result)
    result["trajectory"] = world.events
    result["security_log"] = world.security_log
    return result


# --- disk loading --------------------------------------------------------

def _load_callable(path: Path, attr: str) -> Any:
    mod_name = f"reddust_dyn_{path.parent.name}_{path.stem}"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, attr)


def load_inputs(task_dir: Path) -> dict:
    """Load every ``*.json`` under inputs/ as ``inputs[<stem>]``; expose the
    inputs directory path as ``inputs["_dir"]`` for binary assets (images)."""
    inputs: dict = {}
    idir = task_dir / "inputs"
    if idir.exists():
        inputs["_dir"] = str(idir)
        for jf in sorted(idir.glob("*.json")):
            inputs[jf.stem] = json.loads(jf.read_text(encoding="utf-8"))
    edir = task_dir / "expected"
    if edir.exists():
        inputs["_expected_dir"] = str(edir)
        for jf in sorted(edir.glob("*.json")):
            inputs[f"expected_{jf.stem}"] = json.loads(jf.read_text(encoding="utf-8"))
    return inputs


def run_task_dir(task_dir: str | Path, solution: str = "gold") -> dict:
    """Run ``solutions/<solution>.py`` for the task at ``task_dir``."""
    task_dir = Path(task_dir)
    spec = yaml.safe_load((task_dir / "task.yaml").read_text(encoding="utf-8"))
    inputs = load_inputs(task_dir)
    build_tools = _load_callable(task_dir / "tools.py", "build_tools")
    verify = _load_callable(task_dir / "verifier" / "verify.py", "verify")
    solve = _load_callable(task_dir / "solutions" / f"{solution}.py", "solve")
    return run_solution(spec, inputs, build_tools, solve, verify)
