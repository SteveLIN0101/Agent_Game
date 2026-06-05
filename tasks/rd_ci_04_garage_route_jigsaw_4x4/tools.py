"""Deep grader (family=jigsaw) for rd_ci_04_garage_route_jigsaw_4x4 — dispatches to openclaw.reddust.deeplib.
Domain data: inputs/data.json · answer key: expected/key.json."""
from openclaw.reddust.deeplib import build_tools_for


def build_tools(world):
    return build_tools_for(world)
