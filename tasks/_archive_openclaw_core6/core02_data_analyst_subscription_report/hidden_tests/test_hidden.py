"""Hidden tests for subscription report task."""
import json
import pytest
from pathlib import Path

OUTPUT_DIR = Path('/workspace/outputs')
GOLD = Path('/opt/verifier/expected/gold.json')


def load_actual():
    with open(OUTPUT_DIR / 'summary.json') as f:
        return json.load(f)


def load_gold():
    return json.loads(GOLD.read_text())


class TestHiddenMRR:
    def test_mrr_within_tolerance(self):
        actual = load_actual()
        gold = load_gold()
        assert abs(actual['mrr'] - gold['mrr']) <= 0.01, \
            f"MRR mismatch: expected {gold['mrr']}, got {actual['mrr']}"

    def test_new_mrr_within_tolerance(self):
        actual = load_actual()
        gold = load_gold()
        assert abs(actual['new_mrr'] - gold['new_mrr']) <= 0.01

    def test_churned_mrr_within_tolerance(self):
        actual = load_actual()
        gold = load_gold()
        assert abs(actual['churned_mrr'] - gold['churned_mrr']) <= 0.01

    def test_net_mrr_growth_within_tolerance(self):
        actual = load_actual()
        gold = load_gold()
        assert abs(actual['net_mrr_growth'] - gold['net_mrr_growth']) <= 0.01


class TestHiddenChurn:
    def test_top_churn_segments_correct(self):
        actual = load_actual()
        gold = load_gold()
        assert actual['top_churn_segments'] == gold['top_churn_segments'], \
            f"Top churn segments mismatch"

    def test_top_churn_segments_count(self):
        actual = load_actual()
        assert len(actual['top_churn_segments']) == 3, \
            f"Expected 3 top churn segments, got {len(actual['top_churn_segments'])}"
