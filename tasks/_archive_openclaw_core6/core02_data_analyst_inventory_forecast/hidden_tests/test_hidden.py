"""Hidden tests for inventory forecast."""
import json

def test_moving_averages_positive():
    with open('/workspace/outputs/forecast.json') as f:
        data = json.load(f)
    for p in data['products']:
        assert p['ma7'] > 0
        assert p['ma30'] > 0

def test_ma7_and_ma30_different():
    with open('/workspace/outputs/forecast.json') as f:
        data = json.load(f)
    for p in data['products']:
        assert p['ma7'] != p['ma30'], f"ma7 and ma30 should differ for {p['product_id']}"
