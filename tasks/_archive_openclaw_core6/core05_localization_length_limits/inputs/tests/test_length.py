"""Tests for length limits."""
import json
from pathlib import Path

def test_outputs_exist():
    assert (Path('/workspace/output/strings_zh.json')).exists()

def test_all_within_limits():
    with open('/workspace/reference/length_limits.json') as f:
        limits = json.load(f)
    with open('/workspace/output/strings_zh.json') as f:
        tgt = json.load(f)
    violations = []
    for key, max_chars in limits.items():
        if key in tgt and len(tgt[key]) > max_chars:
            violations.append(f"{key}: {len(tgt[key])} > {max_chars}")
    assert not violations, "\n".join(violations)
