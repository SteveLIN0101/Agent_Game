#!/usr/bin/env python
"""Bind a Red Dust task to a deep-grading *family* harness (openclaw.reddust.deeplib).

Given a task dir + family name, this writes the four tiny dispatch shims
(tools.py / verifier/verify.py / solutions/gold.py / solutions/bad.py) and stamps
``family`` into inputs/brief.json. The per-task *content* lives in
``inputs/data.json`` + ``expected/key.json`` (authored separately); this script
only wires the plumbing so every deep task shares one tested engine.

Usage:
    python scripts/bind_deep_family.py tasks/rd_sa_04_fake_warden_authority safety
    python scripts/bind_deep_family.py --all            # rebind every bound task
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SHIM_TOOLS = '''"""Deep grader (family={fam}) for {tid} — dispatches to openclaw.reddust.deeplib.
Domain data: inputs/data.json · answer key: expected/key.json."""
from openclaw.reddust.deeplib import build_tools_for


def build_tools(world):
    return build_tools_for(world)
'''

SHIM_VERIFY = '''"""Deep grader (family={fam}) for {tid} — grades domain correctness vs key."""
from openclaw.reddust.deeplib import verify_for


def verify(world):
    return verify_for(world)
'''

SHIM_GOLD = '''"""Reference gold solution for {tid} (family={fam}) -> ~100."""
from openclaw.reddust.deeplib import gold_for


def solve(tools, world):
    return gold_for(tools, world)
'''

SHIM_BAD = '''"""Reference bad solution for {tid} (family={fam}) -> critically capped."""
from openclaw.reddust.deeplib import bad_for


def solve(tools, world):
    return bad_for(tools, world)
'''


def bind(task_dir: Path, family: str) -> None:
    task_dir = Path(task_dir)
    brief_path = task_dir / "inputs" / "brief.json"
    brief = json.loads(brief_path.read_text(encoding="utf-8")) if brief_path.exists() else {}
    tid = brief.get("id") or task_dir.name
    brief["family"] = family
    brief_path.parent.mkdir(parents=True, exist_ok=True)
    brief_path.write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")

    fmt = {"fam": family, "tid": tid}
    (task_dir / "tools.py").write_text(SHIM_TOOLS.format(**fmt), encoding="utf-8")
    (task_dir / "verifier").mkdir(exist_ok=True)
    (task_dir / "verifier" / "verify.py").write_text(SHIM_VERIFY.format(**fmt), encoding="utf-8")
    (task_dir / "solutions").mkdir(exist_ok=True)
    (task_dir / "solutions" / "gold.py").write_text(SHIM_GOLD.format(**fmt), encoding="utf-8")
    (task_dir / "solutions" / "bad.py").write_text(SHIM_BAD.format(**fmt), encoding="utf-8")
    print(f"bound {task_dir.name} -> family={family}")


def is_bound(task_dir: Path) -> str | None:
    """Return the family a task is already bound to (reads brief.json), else None."""
    bp = Path(task_dir) / "inputs" / "brief.json"
    if not bp.exists():
        return None
    return json.loads(bp.read_text(encoding="utf-8")).get("family")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--all":
        for d in sorted((ROOT / "tasks").glob("rd_*")):
            fam = is_bound(d)
            if fam:
                bind(d, fam)
    elif len(sys.argv) == 3:
        bind(ROOT / sys.argv[1] if not Path(sys.argv[1]).is_absolute() else sys.argv[1],
             sys.argv[2])
    else:
        print(__doc__)
        sys.exit(1)
