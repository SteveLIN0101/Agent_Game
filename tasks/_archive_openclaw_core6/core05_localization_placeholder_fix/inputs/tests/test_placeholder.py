"""Tests for placeholder fix."""
import json, re
from pathlib import Path

def test_outputs_exist():
    assert (Path('/workspace/output/strings_zh.json')).exists()
    assert (Path('/workspace/output/localization_qa.json')).exists()

def test_all_placeholders_restored():
    with open('/workspace/output/strings_zh.json') as f:
        tgt = json.load(f)
    # Check that curly-brace placeholders are preserved
    text = json.dumps(tgt, ensure_ascii=False)
    assert '{userName}' in text
    assert '{count}' in text
    assert '{itemType}' in text
    assert '{error}' in text

def test_no_chinese_inside_braces():
    with open('/workspace/output/strings_zh.json') as f:
        tgt = json.load(f)
    text = json.dumps(tgt, ensure_ascii=False)
    import re
    bad = re.findall(r'\{[^}]*[\u4e00-\u9fff][^}]*\}', text)
    assert not bad, f"Chinese inside braces: {bad}"
