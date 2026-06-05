"""Reference bad solution for rd_sa_02_access_key_leak_detect (family=safety) -> critically capped."""
from openclaw.reddust.deeplib import bad_for


def solve(tools, world):
    return bad_for(tools, world)
