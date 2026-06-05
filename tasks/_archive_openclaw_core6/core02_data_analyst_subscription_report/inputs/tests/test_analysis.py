"""Visible tests for subscription report analysis."""
import json
import csv
import pytest
from pathlib import Path

DATA_DIR = Path('/workspace/data')
OUTPUT_DIR = Path('/workspace/outputs')


class TestDataLoading:
    def test_customers_csv_exists(self):
        assert (DATA_DIR / 'customers.csv').exists()

    def test_subscriptions_csv_exists(self):
        assert (DATA_DIR / 'subscriptions.csv').exists()

    def test_payments_csv_exists(self):
        assert (DATA_DIR / 'payments.csv').exists()

    def test_cancellations_csv_exists(self):
        assert (DATA_DIR / 'cancellations.csv').exists()


class TestOutputFiles:
    def test_summary_json_exists(self):
        assert (OUTPUT_DIR / 'summary.json').exists(), "outputs/summary.json not found"

    def test_report_md_exists(self):
        assert (OUTPUT_DIR / 'report.md').exists(), "outputs/report.md not found"

    def test_cleaned_payments_exists(self):
        assert (OUTPUT_DIR / 'cleaned_payments.csv').exists(), "outputs/cleaned_payments.csv not found"

    def test_summary_json_has_required_keys(self):
        with open(OUTPUT_DIR / 'summary.json') as f:
            data = json.load(f)
        required = ['week', 'mrr', 'new_mrr', 'churned_mrr', 'net_mrr_growth', 'top_churn_segments']
        for key in required:
            assert key in data, f"Missing key: {key}"

    def test_summary_week_is_w32(self):
        with open(OUTPUT_DIR / 'summary.json') as f:
            data = json.load(f)
        assert data['week'] == '2025-W32'

    def test_top_churn_segments_is_list(self):
        with open(OUTPUT_DIR / 'summary.json') as f:
            data = json.load(f)
        assert isinstance(data['top_churn_segments'], list)


class TestCleanedPayments:
    def test_no_duplicate_transaction_ids(self):
        with open(OUTPUT_DIR / 'cleaned_payments.csv', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        ids = [r['payment_id'] for r in rows]
        assert len(ids) == len(set(ids)), f"Found {len(ids) - len(set(ids))} duplicate payment_ids"

    def test_cleaned_payments_has_required_columns(self):
        with open(OUTPUT_DIR / 'cleaned_payments.csv', newline='') as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames
        for col in ['payment_id', 'customer_id', 'amount', 'currency', 'timestamp']:
            assert col in columns, f"Missing column: {col}"
