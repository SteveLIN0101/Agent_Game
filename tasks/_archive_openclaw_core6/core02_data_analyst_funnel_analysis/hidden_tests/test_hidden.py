"""Hidden tests for funnel analysis."""
import json

def test_conversion_calculation():
    with open('/workspace/outputs/funnel.json') as f:
        data = json.load(f)
    expected = (data['stages']['purchase'] / data['stages']['page_view']) * 100
    assert abs(data['overall_conversion'] - expected) < 1.0

def test_each_stage_positive():
    with open('/workspace/outputs/funnel.json') as f:
        data = json.load(f)
    for s, v in data['stages'].items():
        assert v > 0, f"{s} should be > 0"
