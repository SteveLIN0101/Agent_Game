"""Deep grader (family=search) for rd_sr_04_repair_patch_4searches — dispatches to openclaw.reddust.deeplib.
Domain data: inputs/data.json · answer key: expected/key.json."""
from openclaw.reddust.deeplib import build_tools_for


def build_tools(world):
    return build_tools_for(world)
