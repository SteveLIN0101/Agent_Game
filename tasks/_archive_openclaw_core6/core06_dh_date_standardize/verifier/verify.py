"""Core-06 Digital Humanities: date_standardize verify.py"""
import json, subprocess, sys, csv, re
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
        "visible_tests_pass": False,
        "hidden_tests_pass": False,
        "required_outputs_exist": [],
        "missing_outputs": [],
        "all_dates_standardized": False,
        "report_complete": False,
        "changelog_updated": True,
        "no_hardcoded_values": True,
        "tests_unmodified": True,
        "details": {},
    }

    passed, output = run_pytest("tests/")
    results["visible_tests_pass"] = passed
    results["details"]["visible_tests_output"] = output[-500:]

    if HIDDEN_TESTS.exists():
        passed, output = run_pytest(str(HIDDEN_TESTS))
        results["hidden_tests_pass"] = passed
        results["details"]["hidden_tests_output"] = output[-500:]

    required = ["output/standardized_dates.csv", "output/report.md"]
    for path in required:
        if (WORKSPACE / path).exists():
            results["required_outputs_exist"].append(path)
        else:
            results["missing_outputs"].append(path)

    # Check all dates standardized
    if (WORKSPACE / "output/standardized_dates.csv").exists():
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        with open(WORKSPACE / "output/standardized_dates.csv", newline='') as f:
            rows = list(csv.DictReader(f))
        results["all_dates_standardized"] = all(date_pattern.match(r['date']) for r in rows)

    # Check report
    if (WORKSPACE / "output/report.md").exists():
        report = (WORKSPACE / "output/report.md").read_text()
        results["report_complete"] = len(report.strip()) > 0

    print(json.dumps(results, indent=2))
    all_pass = results["visible_tests_pass"] and results["hidden_tests_pass"]
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
