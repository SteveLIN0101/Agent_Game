"""Deep grader (family=safety) for rd_sa_02_access_key_leak_detect — grades domain correctness vs key."""
from openclaw.reddust.deeplib import verify_for


def verify(world):
    return verify_for(world)
