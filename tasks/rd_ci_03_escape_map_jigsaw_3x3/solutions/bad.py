"""A naive-but-bad trajectory for RD-CI-03 (the failure mode the task tests).

Dumps the first 9 fragments into the grid in filename order without rejecting the
distractors or reasoning about rotation, then draws a straight route that cuts
through a red-sand cell.  Should be critically capped with readable reasons.
"""


def solve(tools, world):
    frags = tools["load_fragments"]()
    ids = [f["id"] for f in frags]
    mapping = {i: {"fragment": ids[i], "rotation": 0} for i in range(9)}
    tools["assemble_grid"](mapping)
    tools["mark_route"]([0, 1, 2, 5, 8])   # cell 2 is 红沙 (impassable)
    tools["export_image"]()
