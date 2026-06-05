"""Tests for funnel analysis."""
import json
from pathlib import Path

def test_outputs_exist():
    assert (Path('/workspace/outputs/funnel.json')).exists()
    assert (Path('/workspace/outputs/report.md')).exists()

def test_funnel_has_stages():
    with open('/workspace/outputs/funnel.json') as f:
        data = json.load(f)
    assert 'stages' in data
    for stage in ['page_view', 'signup', 'add_to_cart', 'purchase']:
        assert stage in data['stages']

def test_funnel_decreases():
    with open('/workspace/outputs/funnel.json') as f:
        data = json.load(f)
    stages = data['stages']
    assert stages['page_view'] >= stages['signup']
    assert stages['signup'] >= stages['add_to_cart']
    assert stages['add_to_cart'] >= stages['purchase']

def test_overall_conversion_is_float():
    with open('/workspace/outputs/funnel.json') as f:
        data = json.load(f)
    assert 'overall_conversion' in data
    assert 0 < data['overall_conversion'] < 100
