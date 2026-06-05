"""Tests for key integrity check."""
import json
from pathlib import Path

def test_keys_match_source():
    with open('/workspace/source/strings_en.json') as f:
        src = json.load(f)
    with open('/workspace/output/strings_zh.json') as f:
        tgt = json.load(f)
    assert set(src.keys()) == set(tgt.keys()), f"Missing: {set(src.keys())-set(tgt.keys())}, Extra: {set(tgt.keys())-set(src.keys())}"
