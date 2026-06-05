"""Tests for archive metadata."""
import csv
from pathlib import Path

def test_metadata_exists():
    assert (Path('/workspace/output/metadata.csv')).exists()

def test_unknown_sender():
    with open('/workspace/output/metadata.csv',newline='') as f:
        rows = list(csv.DictReader(f))
    letter3 = [r for r in rows if r['doc_id']=='letter_003']
    assert letter3, "letter_003 not found"
    assert letter3[0]['sender']=='unknown', f"Expected unknown, got {letter3[0]['sender']}"
