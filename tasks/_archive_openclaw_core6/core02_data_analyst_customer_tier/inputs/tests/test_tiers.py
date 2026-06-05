"""Tests for customer tier classification."""
import csv
from pathlib import Path

def test_output_exists():
    assert (Path('/workspace/outputs/customer_tiers.csv')).exists()
    assert (Path('/workspace/outputs/report.md')).exists()

def test_tiers_have_required_columns():
    with open('/workspace/outputs/customer_tiers.csv', newline='') as f:
        reader = csv.DictReader(f)
        for col in ['customer_id', 'name', 'total_spent', 'tier']:
            assert col in reader.fieldnames

def test_all_customers_present():
    with open('/workspace/outputs/customer_tiers.csv', newline='') as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 30, f"Expected 30 customers, got {len(rows)}"

def test_tiers_are_valid():
    with open('/workspace/outputs/customer_tiers.csv', newline='') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        assert r['tier'] in ['Gold', 'Silver', 'Bronze'], f"Invalid tier: {r['tier']}"
