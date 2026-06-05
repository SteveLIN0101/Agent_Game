"""Deep grader (family=safety) for rd_sa_10_malicious_water_plugin — dispatches to openclaw.reddust.deeplib.
Domain data: inputs/data.json · answer key: expected/key.json."""
from openclaw.reddust.deeplib import build_tools_for


def build_tools(world):
    return build_tools_for(world)
