"""Tests for entity authority matching."""
import csv
from pathlib import Path

def test_output_exists():
    assert (Path('/workspace/output/normalized_entities.csv')).exists()

def test_has_confidence_column():
    with open('/workspace/output/normalized_entities.csv',newline='') as f:
        reader = csv.DictReader(f)
        assert 'confidence' in reader.fieldnames or 'canonical_name' in reader.fieldnames

def test_lq_matched():
    with open('/workspace/output/normalized_entities.csv',newline='') as f:
        rows = list(csv.DictReader(f))
    found = [r for r in rows if 'Liang Qichao' in str(r.values())]
    assert len(found) >= 2
