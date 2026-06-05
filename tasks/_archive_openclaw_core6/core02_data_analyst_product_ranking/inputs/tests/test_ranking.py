"""Tests for product ranking."""
import csv
from pathlib import Path

def test_output_exists():
    assert (Path('/workspace/outputs/product_ranking.csv')).exists()
    assert (Path('/workspace/outputs/report.md')).exists()

def test_ranking_has_columns():
    with open('/workspace/outputs/product_ranking.csv', newline='') as f:
        reader = csv.DictReader(f)
        for col in ['rank', 'product_id', 'product_name', 'total_revenue']:
            assert col in reader.fieldnames

def test_rank_is_dense():
    with open('/workspace/outputs/product_ranking.csv', newline='') as f:
        rows = list(csv.DictReader(f))
    ranks = [int(r['rank']) for r in rows]
    assert ranks[0] == 1
    assert ranks == sorted(ranks)

def test_all_products_ranked():
    with open('/workspace/outputs/product_ranking.csv', newline='') as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 10
