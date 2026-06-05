"""Reference (good-agent) solution for RD-CI-03.

Represents a correct submission: identifies the 9 real tiles (excluding the 6
distractors), reports each tile's rotation, assembles the 3×3 grid, and marks a
connected route that avoids the red-sand cells.  The reference reconstruction is
read from expected/solution.json (the answer key the agent-under-test never sees).
"""
import json
from pathlib import Path

_SOLUTION = Path(__file__).resolve().parent.parent / "expected" / "solution.json"


def solve(tools, world):
    sol = json.loads(_SOLUTION.read_text(encoding="utf-8"))
    frags = tools["load_fragments"]()

    # (illustrative) use the real edge-matching signal before committing
    if len(frags) >= 2:
        tools["compare_edges"](frags[0]["id"], "right", frags[1]["id"], "left")

    mapping = {}
    for fid, info in sol["correct"].items():
        if info["rotation"]:
            tools["rotate_piece"](fid, info["rotation"])
        mapping[info["cell"]] = {"fragment": fid, "rotation": info["rotation"]}

    tools["assemble_grid"](mapping)
    tools["mark_route"](sol["route"])
    tools["export_image"]()
