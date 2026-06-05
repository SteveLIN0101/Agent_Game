"""Tests for inventory forecast."""
import json
from pathlib import Path

def test_outputs_exist():
    assert (Path('/workspace/outputs/forecast.json')).exists()
    assert (Path('/workspace/outputs/report.md')).exists()

def test_forecast_has_products():
    with open('/workspace/outputs/forecast.json') as f:
        data = json.load(f)
    assert 'products' in data
    assert len(data['products']) == 3

def test_forecast_has_moving_averages():
    with open('/workspace/outputs/forecast.json') as f:
        data = json.load(f)
    for p in data['products']:
        assert 'ma7' in p
        assert 'ma30' in p
