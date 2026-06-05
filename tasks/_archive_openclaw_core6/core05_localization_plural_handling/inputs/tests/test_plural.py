"""Tests for plural handling."""
import json
from pathlib import Path

def test_count_placeholder_preserved():
    with open('/workspace/output/strings_zh.json') as f:
        tgt = json.load(f)
    text = json.dumps(tgt, ensure_ascii=False)
    assert '{count}' in text

def test_no_english_plural_forms():
    """Chinese shouldn't use 们 for non-person plurals."""
    with open('/workspace/output/strings_zh.json') as f:
        tgt = json.load(f)
    text = json.dumps(tgt, ensure_ascii=False)
    # files shouldn't become 文件们
    assert '文件们' not in text
    assert '任务们' not in text
