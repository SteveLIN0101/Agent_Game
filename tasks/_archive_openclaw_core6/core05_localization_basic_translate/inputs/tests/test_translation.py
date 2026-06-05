"""Tests for basic translation task."""
import json
from pathlib import Path

WORKSPACE = Path('/workspace')


def load_source():
    with open(WORKSPACE / 'source/strings_en.json') as f:
        return json.load(f)


def load_target():
    with open(WORKSPACE / 'output/strings_zh.json') as f:
        return json.load(f)


def test_output_exists():
    assert (WORKSPACE / 'output/strings_zh.json').exists(), "output/strings_zh.json not found"


def test_qa_report_exists():
    assert (WORKSPACE / 'output/localization_qa.json').exists(), "output/localization_qa.json not found"


def test_all_keys_present():
    src = load_source()
    tgt = load_target()
    src_keys = set(src.keys())
    tgt_keys = set(tgt.keys())
    missing = src_keys - tgt_keys
    extra = tgt_keys - src_keys
    assert not missing, f"Missing keys: {missing}"
    assert not extra, f"Extra keys: {extra}"


def test_placeholders_preserved():
    src = load_source()
    tgt = load_target()
    import re
    placeholder_pattern = re.compile(r'\{[^}]+\}|%s|%d|%\w+')
    issues = []
    for key in src:
        src_placeholders = set(placeholder_pattern.findall(src[key]))
        tgt_placeholders = set(placeholder_pattern.findall(tgt[key]))
        if src_placeholders != tgt_placeholders:
            issues.append(f"{key}: src={src_placeholders}, tgt={tgt_placeholders}")
    assert not issues, f"Placeholder mismatches:\n" + "\n".join(issues)


def test_workspace_translated_correctly():
    tgt = load_target()
    # workspace should be translated as 工作区, not 空间站
    text = json.dumps(tgt, ensure_ascii=False)
    assert '工作区' in text, "workspace should be translated as 工作区"


def test_not_empty():
    tgt = load_target()
    for key, value in tgt.items():
        assert len(value.strip()) > 0, f"Empty translation for key: {key}"
