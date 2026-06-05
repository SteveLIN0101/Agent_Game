"""Tests for multi-source KPI dashboard."""
import json
from pathlib import Path

KPI_KEYS = ['total_revenue', 'avg_order_value', 'clv', 'churn_rate', 'repeat_purchase_rate', 'profit_margin']

def test_outputs_exist():
    assert (Path('/workspace/outputs/kpi_dashboard.json')).exists()
    assert (Path('/workspace/outputs/report.md')).exists()

def test_all_kpis_present():
    with open('/workspace/outputs/kpi_dashboard.json') as f:
        data = json.load(f)
    for k in KPI_KEYS:
        assert k in data, f"Missing KPI: {k}"

def test_kpis_are_reasonable():
    with open('/workspace/outputs/kpi_dashboard.json') as f:
        data = json.load(f)
    assert data['total_revenue'] > 0
    assert 0 < data['profit_margin'] < 100
    assert 0 < data['churn_rate'] < 100
