"""Hidden tests for anomaly detection."""
import json

def test_iqr_positive():
    with open('/workspace/outputs/anomalies.json') as f:
        data = json.load(f)
    assert data['IQR'] > 0

def test_bounds_correct():
    with open('/workspace/outputs/anomalies.json') as f:
        data = json.load(f)
    assert abs(data['lower_bound'] - (data['Q1'] - 1.5 * data['IQR'])) < 0.1
    assert abs(data['upper_bound'] - (data['Q3'] + 1.5 * data['IQR'])) < 0.1
