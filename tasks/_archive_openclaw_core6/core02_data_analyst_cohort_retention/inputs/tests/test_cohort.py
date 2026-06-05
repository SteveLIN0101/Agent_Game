"""Tests for cohort retention analysis."""
import json
from pathlib import Path

def test_outputs_exist():
    assert (Path('/workspace/outputs/retention.json')).exists()
    assert (Path('/workspace/outputs/report.md')).exists()

def test_retention_has_cohorts():
    with open('/workspace/outputs/retention.json') as f:
        data = json.load(f)
    assert 'cohorts' in data
    assert len(data['cohorts']) > 0

def test_retention_values_are_percentages():
    with open('/workspace/outputs/retention.json') as f:
        data = json.load(f)
    for c in data['cohorts']:
        assert 0 <= c['d1'] <= 100
        assert 0 <= c['d7'] <= 100
        assert 0 <= c['d30'] <= 100
