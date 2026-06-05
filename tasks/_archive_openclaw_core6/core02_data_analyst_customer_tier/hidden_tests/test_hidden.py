"""Hidden tests for customer tiers."""
import csv

def test_gold_tier_threshold():
    with open('/workspace/outputs/customer_tiers.csv', newline='') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        spent = float(r['total_spent'])
        if r['tier'] == 'Gold':
            assert spent >= 10000, f"Gold customer {r['customer_id']} spent only {spent}"

def test_silver_tier_range():
    with open('/workspace/outputs/customer_tiers.csv', newline='') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        spent = float(r['total_spent'])
        if r['tier'] == 'Silver':
            assert 5000 <= spent < 10000, f"Silver customer {r['customer_id']} spent {spent}"

def test_zero_spend_is_bronze():
    with open('/workspace/outputs/customer_tiers.csv', newline='') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        if float(r['total_spent']) == 0:
            assert r['tier'] == 'Bronze'
