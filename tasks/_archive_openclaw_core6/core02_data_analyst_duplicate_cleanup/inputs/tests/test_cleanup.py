"""Tests for duplicate cleanup."""
import csv
from pathlib import Path

def test_output_exists():
    assert (Path('/workspace/outputs/cleaned_payments.csv')).exists()
    assert (Path('/workspace/outputs/report.md')).exists()

def test_no_duplicate_payment_ids():
    with open('/workspace/outputs/cleaned_payments.csv', newline='') as f:
        rows = list(csv.DictReader(f))
    ids = [r['payment_id'] for r in rows]
    assert len(ids) == len(set(ids)), f"Found {len(ids)-len(set(ids))} duplicates"

def test_fewer_rows_than_input():
    with open('/workspace/outputs/cleaned_payments.csv', newline='') as f:
        cleaned = len(list(csv.DictReader(f)))
    with open('/workspace/data/payments.csv', newline='') as f:
        original = len(list(csv.DictReader(f)))
    assert cleaned < original, f"Expected fewer rows, got {cleaned} vs {original}"

def test_report_has_stats():
    report = (Path('/workspace/outputs/report.md')).read_text()
    assert 'clean' in report.lower() or 'duplicat' in report.lower() or '去除' in report.lower()
