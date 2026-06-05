"""Tests for glossary compliance."""
import json
from pathlib import Path

def test_forbidden_words_removed():
    with open('/workspace/output/strings_zh.json') as f:
        tgt = json.load(f)
    text = json.dumps(tgt, ensure_ascii=False)
    assert '空间站' not in text
    assert '开票系统' not in text
    assert '模版' not in text

def test_workspace_correct():
    with open('/workspace/output/strings_zh.json') as f:
        tgt = json.load(f)
    for v in tgt.values():
        if '工作区' in v:
            break
    else:
        assert False, "workspace should use 工作区"
