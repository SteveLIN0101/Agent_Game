"""Tests for QA audit."""
import json
from pathlib import Path

def test_outputs_exist():
    assert (Path('/workspace/output/strings_zh_fixed.json')).exists()
    assert (Path('/workspace/output/localization_qa.json')).exists()

def test_keys_match_source():
    with open('/workspace/source/strings_en.json') as f: src=json.load(f)
    with open('/workspace/output/strings_zh_fixed.json') as f: tgt=json.load(f)
    assert set(src.keys())==set(tgt.keys())

def test_qa_report_has_issues():
    with open('/workspace/output/localization_qa.json') as f:
        qa = json.load(f)
    assert len(qa) > 0
