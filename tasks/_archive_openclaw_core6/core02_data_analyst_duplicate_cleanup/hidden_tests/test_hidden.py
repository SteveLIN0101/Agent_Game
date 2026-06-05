"""Hidden tests for duplicate cleanup."""
import csv

def test_latest_timestamp_kept():
    with open('/workspace/outputs/cleaned_payments.csv', newline='') as f:
        rows = {r['payment_id']: r for r in csv.DictReader(f)}
    # PAY-00001 had a duplicate with older timestamp
    assert 'PAY-00001' in rows
    assert '2025-08' in rows['PAY-00001']['timestamp']

def test_exactly_30_rows():
    with open('/workspace/outputs/cleaned_payments.csv', newline='') as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 30, f"Expected 30 unique payments, got {len(rows)}"
