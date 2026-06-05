"""Tests for gazetteer-based NER."""
import csv
from pathlib import Path

def test_output_exists():
    assert (Path('/workspace/output/extracted_places.csv')).exists()

def test_has_context_column():
    with open('/workspace/output/extracted_places.csv',newline='') as f:
        reader = csv.DictReader(f)
        assert 'canonical_place' in reader.fieldnames

def test_beijing_found():
    with open('/workspace/output/extracted_places.csv',newline='') as f:
        rows = list(csv.DictReader(f))
    places = [r.get('canonical_place','') for r in rows]
    assert 'Beijing' in places, f"Beijing not in {places}"
