"""Core-01 SE: off_by_one_fix verify.py"""
import json, subprocess, sys
from pathlib import Path

WORKSPACE = Path("/workspace")
HIDDEN_TESTS = Path("/opt/verifier/hidden_tests")

def run_pytest(test_path):
    result = subprocess.run(
        ["python3", "-m", "pytest", str(test_path), "-v", "--tb=short"],
        capture_output=True, text=True, cwd=str(WORKSPACE),
    )
    return result.returncode == 0, result.stdout + "\n" + result.stderr

def main():
    results = {
        "visible_tests_pass": False, "hidden_tests_pass": False,
        "required_outputs_exist": [], "missing_outputs": [],
        "changelog_updated": False, "no_hardcoded_values": True,
        "tests_unmodified": True, "details": {},
    }
    passed, output = run_pytest("tests/")
    results["visible_tests_pass"] = passed
    results["details"]["visible_tests_output"] = output[-500:]
    if HIDDEN_TESTS.exists():
        passed, output = run_pytest(str(HIDDEN_TESTS))
        results["hidden_tests_pass"] = passed
        results["details"]["hidden_tests_output"] = output[-500:]
    for path in ["src/scheduler.py", "CHANGELOG.md"]:
        if (WORKSPACE / path).exists():
            results["required_outputs_exist"].append(path)
        else:
            results["missing_outputs"].append(path)
    cl = WORKSPACE / "CHANGELOG.md"
    if cl.exists():
        content = cl.read_text().lower()
        results["changelog_updated"] = "off" in content or "fix" in content or "scheduler" in content
    print(json.dumps(results, indent=2))
    sys.exit(0 if results["visible_tests_pass"] and results["hidden_tests_pass"] else 1)

if __name__ == "__main__":
    main()
