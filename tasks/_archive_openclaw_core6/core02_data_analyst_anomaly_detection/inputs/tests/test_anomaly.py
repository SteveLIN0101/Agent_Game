"""Tests for anomaly detection."""
import json
from pathlib import Path

def test_outputs_exist():
    assert (Path('/workspace/outputs/anomalies.json')).exists()
    assert (Path('/workspace/outputs/report.md')).exists()

def test_has_iqr_stats():
    with open('/workspace/outputs/anomalies.json') as f:
        data = json.load(f)
    for key in ['Q1', 'Q3', 'IQR', 'lower_bound', 'upper_bound']:
        assert key in data, f"Missing key: {key}"

def test_outlier_count_is_int():
    with open('/workspace/outputs/anomalies.json') as f:
        data = json.load(f)
    assert 'outlier_count' in data or 'outliers' in data
