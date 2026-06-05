"""Hidden tests for cohort retention."""
import json

def test_retention_decreases():
    with open('/workspace/outputs/retention.json') as f:
        data = json.load(f)
    for c in data['cohorts']:
        assert c['d1'] >= c['d7'], f"D1 should be >= D7 for cohort {c}"
        assert c['d7'] >= c['d30'], f"D7 should be >= D30 for cohort {c}"

def test_at_least_2_cohorts():
    with open('/workspace/outputs/retention.json') as f:
        data = json.load(f)
    assert len(data['cohorts']) >= 2
