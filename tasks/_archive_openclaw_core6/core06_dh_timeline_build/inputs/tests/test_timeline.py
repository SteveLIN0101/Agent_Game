"""Tests for timeline."""
import csv
from pathlib import Path

def test_timeline_exists():
    assert (Path('/workspace/output/timeline.csv')).exists()

def test_sorted_by_date():
    with open('/workspace/output/timeline.csv',newline='') as f:
        rows = list(csv.DictReader(f))
    dates = [r['date'] for r in rows]
    assert dates == sorted(dates), f"Not sorted: {dates}"

def test_dates_are_iso():
    with open('/workspace/output/timeline.csv',newline='') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        import re
        assert re.match(r'^\d{4}-\d{2}-\d{2}$', r['date'])
