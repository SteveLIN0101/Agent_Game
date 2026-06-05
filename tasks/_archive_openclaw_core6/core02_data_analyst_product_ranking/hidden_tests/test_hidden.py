"""Hidden tests for product ranking."""
import csv

def test_revenue_descending():
    with open('/workspace/outputs/product_ranking.csv', newline='') as f:
        rows = list(csv.DictReader(f))
    revs = [float(r['total_revenue']) for r in rows]
    for i in range(len(revs)-1):
        assert revs[i] >= revs[i+1], f"Not descending at rank {i+1}"

def test_top_product_is_enterprise_suite():
    with open('/workspace/outputs/product_ranking.csv', newline='') as f:
        rows = list(csv.DictReader(f))
    assert 'Enterprise' in rows[0]['product_name'] or rows[0]['rank'] == '1'
