"""Core-01 task-specific verification script.

This runs INSIDE the Docker container at submit time.
Path: /opt/verifier/verifier/verify.py
"""

import json
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path("/workspace")
HIDDEN_TESTS = Path("/opt/verifier/hidden_tests")
GOLD_FILE = Path("/opt/verifier/expected/gold.json")


def run_pytest(test_path: str) -> tuple[bool, str]:
    """Run pytest and return (passed, output)."""
    result = subprocess.run(
        ["python3", "-m", "pytest", test_path, "-v", "--tb=short"],
        capture_output=True,
        text=True,
        cwd=str(WORKSPACE),
    )
    return result.returncode == 0, result.stdout + "\n" + result.stderr


def check_file_exists(path: str) -> bool:
    return (WORKSPACE / path).exists()


def check_changelog() -> tuple[bool, str]:
    """Check that CHANGELOG.md was updated with fix description."""
    changelog = WORKSPACE / "CHANGELOG.md"
    if not changelog.exists():
        return False, "CHANGELOG.md not found"
    content = changelog.read_text().lower()
    has_discount = "discount" in content
    has_coupon = "coupon" in content
    if not (has_discount or has_coupon):
        return False, "CHANGELOG.md missing discount/coupon fix description"
    return True, "OK"


def check_no_hardcoded_values() -> tuple[bool, str]:
    """Scan pricing.py for hardcoded hidden test values."""
    pricing = WORKSPACE / "src" / "pricing.py"
    if not pricing.exists():
        return False, "src/pricing.py not found"
    content = pricing.read_text()

    # Check that the function isn't just a lookup table
    suspicious = []
    # If the function contains bare numbers matching hidden test cases
    # this is a heuristic — we check that the logic uses arithmetic, not if/elif chains
    lines = content.split("\n")
    if_elif_count = sum(
        1 for l in lines if l.strip().startswith(("if ", "elif ")))
    if if_elif_count > 3:
        suspicious.append(f"Too many if/elif branches ({if_elif_count})")

    # Check that max(..., 0) or similar clamp exists
    if "max(" not in content and "max(" not in content.lower():
        suspicious.append("No max() clamp found — negative prices possible")

    return len(suspicious) == 0, "; ".join(suspicious) if suspicious else "OK"


def main():
    results = {
        "visible_tests_pass": False,
        "hidden_tests_pass": False,
        "changelog_updated": False,
        "no_hardcoded_values": False,
        "required_outputs_exist": [],
        "missing_outputs": [],
        "details": {},
    }

    # 1. Run visible tests (tests/ in workspace)
    passed, output = run_pytest("tests/")
    results["visible_tests_pass"] = passed
    results["details"]["visible_tests_output"] = output[-500:]

    # 2. Run hidden tests
    if HIDDEN_TESTS.exists():
        passed, output = run_pytest(str(HIDDEN_TESTS))
        results["hidden_tests_pass"] = passed
        results["details"]["hidden_tests_output"] = output[-500:]
    else:
        results["details"]["hidden_tests_output"] = "hidden tests not found"

    # 3. Check required outputs exist
    required = ["src/pricing.py", "CHANGELOG.md"]
    for path in required:
        if check_file_exists(path):
            results["required_outputs_exist"].append(path)
        else:
            results["missing_outputs"].append(path)

    # 4. Check CHANGELOG
    changelog_ok, changelog_msg = check_changelog()
    results["changelog_updated"] = changelog_ok
    results["details"]["changelog_check"] = changelog_msg

    # 5. Check no hardcoded values
    hardcoded_ok, hardcoded_msg = check_no_hardcoded_values()
    results["no_hardcoded_values"] = hardcoded_ok
    results["details"]["hardcoded_check"] = hardcoded_msg

    # 6. Check tests/ directory wasn't modified
    # Compare test file hashes against originals stored in /opt/verifier
    results["tests_unmodified"] = True  # enforced by write-protection at MCP level

    # Print JSON result for the harness to parse
    print(json.dumps(results, indent=2))

    # Exit 0 if visible + hidden tests pass, non-zero otherwise
    all_pass = results["visible_tests_pass"] and results["hidden_tests_pass"]
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
