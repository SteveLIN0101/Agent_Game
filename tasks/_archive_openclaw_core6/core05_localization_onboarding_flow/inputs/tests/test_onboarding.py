"""Tests for onboarding flow translation."""
import json
from pathlib import Path

def test_all_26_strings():
    with open('/workspace/output/strings_zh.json') as f:
        tgt = json.load(f)
    assert len(tgt) == 26, f"Expected 26 strings, got {len(tgt)}"

def test_no_empty_translations():
    with open('/workspace/output/strings_zh.json') as f:
        tgt = json.load(f)
    for k,v in tgt.items():
        assert len(v.strip())>0, f"Empty: {k}"
