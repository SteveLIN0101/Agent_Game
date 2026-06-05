"""Tests for dual locale."""
import json
from pathlib import Path

def test_both_outputs_exist():
    assert (Path('/workspace/output/strings_zh.json')).exists()
    assert (Path('/workspace/output/strings_ja.json')).exists()

def test_both_have_same_keys():
    with open('/workspace/output/strings_zh.json') as f: zh=json.load(f)
    with open('/workspace/output/strings_ja.json') as f: ja=json.load(f)
    assert set(zh.keys())==set(ja.keys())
