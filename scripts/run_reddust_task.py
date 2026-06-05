#!/usr/bin/env python3
"""Run a Red Dust task end-to-end and print a readable scorecard.

    python scripts/run_reddust_task.py <task_dir> [solution]
    python scripts/run_reddust_task.py tasks/rd_si_01_water_run_negotiation gold
    python scripts/run_reddust_task.py tasks/rd_ci_03_escape_map_jigsaw_3x3 bad

``solution`` defaults to ``gold``; use ``all`` to run every solutions/*.py.
"""
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from openclaw.reddust.engine import run_task_dir  # noqa: E402


def show(task_dir: Path, solution: str) -> None:
    spec = yaml.safe_load((task_dir / "task.yaml").read_text(encoding="utf-8"))
    r = run_task_dir(task_dir, solution)
    print("═" * 64)
    print(f"  {spec['id']} · {spec['title']}   [{solution}]")
    print(f"  目标: {spec['user_visible_goal']}")
    print("─" * 64)
    print(f"  得分 SCORE: {r['score']}/100   "
          f"(可见 {r['visible_score']} · 隐藏 {r['hidden_score']})   "
          f"{'✅ PASS' if r['passed_all'] else '❌ not all checks passed'}")
    print("  检查项:")
    for c in r["checks"]:
        mark = "✓" if c["passed"] else "✗"
        tags = []
        if c["critical"]:
            tags.append("critical")
        if c["hidden"]:
            tags.append("hidden")
        tag = f"  [{', '.join(tags)}]" if tags else ""
        print(f"    {mark} {c['desc']}{tag}")
    card = r["result_card"]
    print(f"  结果卡: 「{card.get('title', '')}」")
    for d in card.get("deltas", []):
        print(f"      · {d}")
    if r["failure_reasons"]:
        print("  失败原因 (≤3):")
        for fr in r["failure_reasons"]:
            print(f"      ✗ {fr}")
    beats = " → ".join(e["beat"] for e in r["trajectory"] if e.get("beat"))
    print(f"  可看懂轨迹: {beats}")
    print("═" * 64)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    task_dir = Path(sys.argv[1])
    solution = sys.argv[2] if len(sys.argv) > 2 else "gold"
    if solution == "all":
        sols = sorted(p.stem for p in (task_dir / "solutions").glob("*.py")
                      if not p.stem.startswith("_"))
        for s in sols:
            show(task_dir, s)
    else:
        show(task_dir, solution)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
