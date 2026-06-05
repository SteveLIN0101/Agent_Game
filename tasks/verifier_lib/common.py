"""Shared verification utilities for OpenClaw task verify.py scripts.

Copy this module into each task's verifier/ directory so verify.py
remains self-contained inside the Docker container.

Usage in verify.py:
    from common import run_pytest, load_gold, compare_json_values, check_csv_schema, ...
"""

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path("/workspace")
HIDDEN_TESTS = Path("/opt/verifier/hidden_tests")
GOLD_FILE = Path("/opt/verifier/expected/gold.json")


# ── Test execution ──────────────────────────────────────────────────────────

def run_pytest(test_path: str, cwd: str = "/workspace") -> tuple[bool, str]:
    """Run pytest and return (passed, combined_output)."""
    result = subprocess.run(
        ["python3", "-m", "pytest", test_path, "-v", "--tb=short"],
        capture_output=True, text=True, cwd=cwd,
    )
    return result.returncode == 0, result.stdout + "\n" + result.stderr


def run_script(script_path: str, cwd: str = "/workspace") -> tuple[bool, str, str]:
    """Run a Python script and return (passed, stdout, stderr)."""
    result = subprocess.run(
        ["python3", script_path],
        capture_output=True, text=True, cwd=cwd,
    )
    return result.returncode == 0, result.stdout, result.stderr


# ── File checks ─────────────────────────────────────────────────────────────

def check_file_exists(path: str) -> bool:
    """Check if a file exists in the workspace."""
    return (WORKSPACE / path).exists()


def read_workspace_file(path: str) -> str:
    """Read file content from workspace."""
    return (WORKSPACE / path).read_text(encoding="utf-8", errors="replace")


def check_file_hash(path: str, expected_hash: str) -> bool:
    """Verify sha256 hash of a file."""
    content = read_workspace_file(path)
    actual = hashlib.sha256(content.encode()).hexdigest()
    return actual == expected_hash


# ── Gold data loading ───────────────────────────────────────────────────────

def load_gold() -> dict:
    """Load the gold.json expected output."""
    if not GOLD_FILE.exists():
        return {}
    return json.loads(GOLD_FILE.read_text())


# ── Numeric comparison ──────────────────────────────────────────────────────

def compare_float(actual: float, expected: float, tolerance: float = 0.01) -> bool:
    """Compare two floats within tolerance."""
    return abs(actual - expected) <= tolerance


def compare_json_values(actual: dict, expected: dict,
                        tolerance: float = 0.01) -> tuple[bool, list[str]]:
    """Compare numeric values in two JSON dicts. Returns (all_match, diffs)."""
    diffs = []
    for key in expected:
        if key not in actual:
            diffs.append(f"Missing key: {key}")
            continue
        a_val = actual[key]
        e_val = expected[key]
        if isinstance(e_val, (int, float)) and isinstance(a_val, (int, float)):
            if not compare_float(float(a_val), float(e_val), tolerance):
                diffs.append(f"{key}: expected {e_val}, got {a_val}")
        elif isinstance(e_val, list) and isinstance(a_val, list):
            if a_val != e_val:
                diffs.append(f"{key}: expected {e_val}, got {a_val}")
        elif a_val != e_val:
            diffs.append(f"{key}: expected {e_val}, got {a_val}")

    for key in actual:
        if key not in expected:
            diffs.append(f"Extra key: {key}")

    return len(diffs) == 0, diffs


# ── CSV utilities ───────────────────────────────────────────────────────────

def check_csv_schema(path: str, expected_columns: list[str]) -> tuple[bool, list[str]]:
    """Verify CSV file has expected columns."""
    full_path = WORKSPACE / path
    if not full_path.exists():
        return False, [f"File not found: {path}"]
    with open(full_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, [])
    missing = [c for c in expected_columns if c not in header]
    extra = [c for c in header if c not in expected_columns]
    issues = []
    if missing:
        issues.append(f"Missing columns: {missing}")
    if extra:
        issues.append(f"Extra columns: {extra}")
    return len(issues) == 0, issues


def read_csv_as_dicts(path: str) -> list[dict]:
    """Read a CSV file into a list of dicts."""
    full_path = WORKSPACE / path
    if not full_path.exists():
        return []
    with open(full_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def count_csv_rows(path: str) -> int:
    """Count data rows in a CSV file (excluding header)."""
    full_path = WORKSPACE / path
    if not full_path.exists():
        return -1
    with open(full_path, newline="", encoding="utf-8") as f:
        return sum(1 for _ in f) - 1


# ── Text content checks ─────────────────────────────────────────────────────

def check_content_contains(path: str, keywords: list[str],
                          case_sensitive: bool = False) -> tuple[bool, list[str]]:
    """Check that file content contains all given keywords."""
    content = read_workspace_file(path)
    if not case_sensitive:
        content = content.lower()
    missing = []
    for kw in keywords:
        target = kw if case_sensitive else kw.lower()
        if target not in content:
            missing.append(kw)
    return len(missing) == 0, missing


def check_content_not_contain(path: str, forbidden: list[str],
                              case_sensitive: bool = False) -> tuple[bool, list[str]]:
    """Check that file content does NOT contain forbidden strings."""
    content = read_workspace_file(path)
    if not case_sensitive:
        content = content.lower()
    found = []
    for kw in forbidden:
        target = kw if case_sensitive else kw.lower()
        if target in content:
            found.append(kw)
    return len(found) == 0, found


# ── JSON utilities ──────────────────────────────────────────────────────────

def load_workspace_json(path: str) -> dict:
    """Load and parse a JSON file from workspace."""
    full_path = WORKSPACE / path
    if not full_path.exists():
        return {}
    return json.loads(full_path.read_text(encoding="utf-8"))


def check_json_keys_match(source_path: str, target_path: str) -> tuple[bool, list[str]]:
    """Check that two JSON files have the same top-level keys."""
    src = load_workspace_json(source_path)
    tgt = load_workspace_json(target_path)
    src_keys = set(src.keys())
    tgt_keys = set(tgt.keys())
    missing = sorted(src_keys - tgt_keys)
    extra = sorted(tgt_keys - src_keys)
    issues = []
    if missing:
        issues.append(f"Missing keys: {missing}")
    if extra:
        issues.append(f"Extra keys: {extra}")
    return len(issues) == 0, issues


# ── Input file integrity ────────────────────────────────────────────────────

def check_input_files_unchanged(original_hashes: dict[str, str]) -> tuple[bool, list[str]]:
    """Verify input files haven't been modified by the agent."""
    modified = []
    for path, expected_hash in original_hashes.items():
        if check_file_exists(path):
            if not check_file_hash(path, expected_hash):
                modified.append(path)
    return len(modified) == 0, modified


# ── Result output ───────────────────────────────────────────────────────────

def dump_result(results: dict) -> None:
    """Print JSON result and exit with appropriate code.

    The MCP server parses stdout as JSON, so this must be the ONLY thing
    printed to stdout.
    """
    print(json.dumps(results, indent=2))

    # Exit code: 0 if all tests pass, 1 otherwise
    visible = results.get("visible_tests_pass", False)
    hidden = results.get("hidden_tests_pass", True)
    all_pass = visible and hidden
    sys.exit(0 if all_pass else 1)
