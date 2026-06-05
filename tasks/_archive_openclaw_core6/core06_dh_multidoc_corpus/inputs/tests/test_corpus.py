"""Tests for multi-doc corpus."""
import csv
from pathlib import Path

def test_outputs_exist():
    assert (Path('/workspace/output/corpus_metadata.csv')).exists()
    assert (Path('/workspace/output/timeline.csv')).exists()

def test_five_docs_in_metadata():
    with open('/workspace/output/corpus_metadata.csv',newline='') as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 5

def test_timeline_ordered():
    with open('/workspace/output/timeline.csv',newline='') as f:
        rows = list(csv.DictReader(f))
    dates = [r['date'] for r in rows]
    assert dates == sorted(dates)
