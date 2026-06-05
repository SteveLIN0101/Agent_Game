"""Deep grader (family=safety) for rd_sa_06_malicious_leaflet_injection — grades domain correctness vs key."""
from openclaw.reddust.deeplib import verify_for


def verify(world):
    return verify_for(world)
