"""Hidden tests for KPI dashboard."""
import json

def test_avg_order_value_positive():
    with open('/workspace/outputs/kpi_dashboard.json') as f:
        data = json.load(f)
    assert data['avg_order_value'] > 0

def test_repeat_rate_between_0_and_100():
    with open('/workspace/outputs/kpi_dashboard.json') as f:
        data = json.load(f)
    assert 0 <= data['repeat_purchase_rate'] <= 100

def test_clv_positive():
    with open('/workspace/outputs/kpi_dashboard.json') as f:
        data = json.load(f)
    assert data['clv'] > 0
