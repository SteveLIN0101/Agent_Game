"""Tests for quarterly sales analysis."""
import json, csv
from pathlib import Path

def test_outputs_exist():
    assert (Path('/workspace/outputs/summary.json')).exists()
    assert (Path('/workspace/outputs/report.md')).exists()

def test_summary_has_all_regions():
    with open('/workspace/outputs/summary.json') as f:
        data = json.load(f)
    for r in ['North', 'South', 'East', 'West']:
        assert r in data, f"Missing region: {r}"

def test_summary_has_quarters():
    with open('/workspace/outputs/summary.json') as f:
        data = json.load(f)
    for r in data:
        for q in ['Q1', 'Q2', 'Q3', 'Q4']:
            assert q in data[r], f"Missing quarter {q} in {r}"

def test_totals_reasonable():
    with open('/workspace/outputs/summary.json') as f:
        data = json.load(f)
    for r in data:
        assert data[r]['total'] > 0
