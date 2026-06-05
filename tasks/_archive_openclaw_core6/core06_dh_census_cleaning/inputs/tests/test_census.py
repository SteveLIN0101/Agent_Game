"""Tests for census cleaning."""
import csv
from pathlib import Path

def test_outputs_exist():
    assert (Path('/workspace/output/cleaned_census.csv')).exists()
    assert (Path('/workspace/output/standardization_report.md')).exists()

def test_dates_standardized():
    with open('/workspace/output/cleaned_census.csv',newline='') as f:
        rows = list(csv.DictReader(f))
    import re
    for r in rows:
        assert re.match(r'^\d{4}-\d{2}-\d{2}$', r['date']), f"Bad date: {r['date']}"

def test_eight_rows():
    with open('/workspace/output/cleaned_census.csv',newline='') as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 8
