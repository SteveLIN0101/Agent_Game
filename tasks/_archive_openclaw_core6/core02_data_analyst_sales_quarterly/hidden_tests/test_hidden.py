"""Hidden tests for quarterly sales."""
import json

def test_q1_is_months_1_2_3():
    with open('/workspace/outputs/summary.json') as f:
        data = json.load(f)
    north_q1 = data['North']['Q1']
    assert north_q1 > 80000 and north_q1 < 120000, f"North Q1 looks wrong: {north_q1}"

def test_all_totals_sum_to_grand_total():
    with open('/workspace/outputs/summary.json') as f:
        data = json.load(f)
    grand = sum(data[r]['total'] for r in data)
    assert grand > 1000000, f"Grand total too low: {grand}"
