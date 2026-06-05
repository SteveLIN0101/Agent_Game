"""Tests for entity extraction."""
import csv
from pathlib import Path

def test_metadata_exists():
    assert (Path('/workspace/output/metadata.csv')).exists()

def test_correct_columns():
    with open('/workspace/output/metadata.csv',newline='') as f:
        reader = csv.DictReader(f)
        for col in ['doc_id','sender','recipient','date','place']:
            assert col in reader.fieldnames

def test_dates_are_iso():
    with open('/workspace/output/metadata.csv',newline='') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        assert len(r['date'])==10, f"Date {r['date']} not YYYY-MM-DD"
