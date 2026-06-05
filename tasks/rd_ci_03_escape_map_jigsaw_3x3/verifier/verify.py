"""Grader for RD-CI-03 — checks the agent's reconstruction against the key.

Visible checks mirror task.yaml's success_checks (grid 3×3, 6 distractors
excluded, transform correctness ≥0.8, route connected).  Grid integrity and
distractor exclusion are *critical*: a map built from the wrong pieces is
worse than no map, so it hard-caps the score.
"""
import json
from pathlib import Path

from openclaw.reddust.checks import Check

_SOLUTION = Path(__file__).resolve().parent.parent / "expected" / "solution.json"


def verify(world):
    sol = json.loads(_SOLUTION.read_text(encoding="utf-8"))
    correct = sol["correct"]                       # {frag_id: {cell, rotation}}
    distractors = set(sol["distractors"])
    impassable = set(sol["impassable_cells"])
    start, end = sol["start"], sol["end"]
    exp_by_cell = {v["cell"]: (fid, v["rotation"]) for fid, v in correct.items()}

    assembly = {int(c): v for c, v in (world.artifact("assembly") or {}).items()}
    route = world.artifact("route") or []
    used_ids = [v.get("fragment") for v in assembly.values()]

    grid_3x3 = set(assembly.keys()) == set(range(9))
    used_distractor = any(fid in distractors for fid in used_ids)
    distractors_excluded = (not used_distractor) and len(set(used_ids)) == 9

    good = sum(
        1 for cell, v in assembly.items()
        if exp_by_cell.get(cell)
        and v.get("fragment") == exp_by_cell[cell][0]
        and int(v.get("rotation", 0)) == int(exp_by_cell[cell][1])
    )
    rate = good / 9.0

    def adjacent(a, b):
        ra, ca = divmod(a, 3)
        rb, cb = divmod(b, 3)
        return abs(ra - rb) + abs(ca - cb) == 1

    route_ok = (
        len(route) >= 2 and route[0] == start and route[-1] == end
        and all(c not in impassable for c in route)
        and all(adjacent(route[i], route[i + 1]) for i in range(len(route) - 1))
    )

    return [
        Check("grid_3x3", "拼成完整的 3×3 楼道图", grid_3x3, 1.5, critical=True,
              fail_reason="没有拼成完整的 3×3 楼道图"),
        Check("distractors_excluded", "排除了 6 张干扰碎片", distractors_excluded,
              1.5, critical=True,
              fail_reason="把干扰碎片当成了真地图的一部分"),
        Check("transforms_correct", "碎片位置/旋转正确率 ≥ 0.8", rate >= 0.8, 2.0,
              fail_reason=f"碎片位置或旋转错得太多（正确率 {rate:.0%} < 80%）"),
        Check("route_connected", "标出从起点到终点、绕开红沙的连通路线", route_ok,
              2.0, fail_reason="逃生路线断了或穿过了红沙危险区"),
        Check("exported", "导出了拼好的地图图片", bool(world.artifact("export")),
              0.5, hidden=True, fail_reason="没有导出拼好的地图"),
    ]
