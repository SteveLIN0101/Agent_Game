"""Deep grader (family=jigsaw) for rd_ci_05_station_coord_jigsaw_5x5 — dispatches to openclaw.reddust.deeplib.
Domain data: inputs/data.json · answer key: expected/key.json."""
from openclaw.reddust.deeplib import build_tools_for


def build_tools(world):
    return build_tools_for(world)
