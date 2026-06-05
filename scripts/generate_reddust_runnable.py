#!/usr/bin/env python3
"""Make every `tasks/rd_*` task runnable + auto-scored by the agent bridge.

For each task that doesn't already have a *bespoke* tools.py (RD-SI-01, RD-CI-03),
write tiny shims onto the shared generic scaffold:

    inputs/brief.json        # available_tools + critical_beats + goal/scenario/grader
    tools.py                 # build_tools -> build_generic_tools
    verifier/verify.py       # verify -> generic_verify
    solutions/gold.py        # solve = generic_gold   (exercises the trajectory → ~100)
    solutions/bad.py         # solve = generic_bad     (does almost nothing → capped)

Bespoke tasks (deep tools.py + verifier) are left untouched.
"""
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "tasks"

TOOLS_SHIM = '''\
"""Generic scaffold tools for {tid} (trajectory/output conformance).
Upgrade to a bespoke tools.py for deep domain grading (cf. RD-SI-01)."""
from openclaw.reddust.generic import build_generic_tools


def build_tools(world):
    return build_generic_tools(world)
'''

VERIFY_SHIM = '''\
"""Generic scaffold grader for {tid}. Upgrade to deep checks per task."""
from openclaw.reddust.generic import generic_verify


def verify(world):
    return generic_verify(world)
'''

GOLD_SHIM = ('"""Reference good run for {tid}: exercises the readable trajectory."""\n'
             "from openclaw.reddust.generic import generic_gold as solve  # noqa: F401\n")
BAD_SHIM = ('"""Bad run for {tid}: does almost nothing — should be capped."""\n'
            "from openclaw.reddust.generic import generic_bad as solve  # noqa: F401\n")


def is_bespoke(task_dir: Path) -> bool:
    tp = task_dir / "tools.py"
    return tp.exists() and "build_generic_tools" not in tp.read_text(encoding="utf-8")


def main() -> int:
    dirs = sorted(d for d in TASKS.glob("rd_*") if (d / "task.yaml").exists())
    generated = skipped = 0
    for d in dirs:
        if is_bespoke(d):
            skipped += 1
            continue
        spec = yaml.safe_load((d / "task.yaml").read_text(encoding="utf-8"))
        tid = spec["id"]
        brief = {
            "goal": spec.get("user_visible_goal", ""),
            "available_tools": spec.get("available_tools", []),
            "critical_beats_for_replay": spec.get("critical_beats_for_replay", []),
            "scenario": spec.get("red_dust_scenario", ""),
            "grader": spec.get("grader_oneliner", ""),
        }
        (d / "inputs").mkdir(exist_ok=True)
        (d / "verifier").mkdir(exist_ok=True)
        (d / "solutions").mkdir(exist_ok=True)
        (d / "inputs" / "brief.json").write_text(
            json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
        (d / "tools.py").write_text(TOOLS_SHIM.format(tid=tid), encoding="utf-8")
        (d / "verifier" / "verify.py").write_text(VERIFY_SHIM.format(tid=tid), encoding="utf-8")
        (d / "solutions" / "gold.py").write_text(GOLD_SHIM.format(tid=tid), encoding="utf-8")
        (d / "solutions" / "bad.py").write_text(BAD_SHIM.format(tid=tid), encoding="utf-8")
        generated += 1
    print(f"generated scaffold for {generated} tasks, skipped {skipped} bespoke, "
          f"total {len(dirs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
