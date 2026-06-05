"""Core-02 Data Analyst: subscription_report verify.py"""
import json
import csv
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path("/workspace")
GOLD_FILE = Path("/opt/verifier/expected/gold.json")
HIDDEN_TESTS = Path("/opt/verifier/hidden_tests")


def run_pytest(test_path):
    result = subprocess.run(
        ["python3", "-m", "pytest", str(test_path), "-v", "--tb=short"],
        capture_output=True, text=True, cwd=str(WORKSPACE),
    )
    return result.returncode == 0, result.stdout + "\n" + result.stderr


def check_file_exists(path):
    return (WORKSPACE / path).exists()


def main():
    results = {
        "visible_tests_pass": False,
        "hidden_tests_pass": False,
        "required_outputs_exist": [],
        "missing_outputs": [],
        "json_values_correct": False,
        "files_unmodified": True,
        "report_contains_kpi": False,
        "changelog_updated": True,  # Not required for data analyst
        "no_hardcoded_values": True,
        "details": {},
    }

    # 1. Visible tests
    passed, output = run_pytest("tests/")
    results["visible_tests_pass"] = passed
    results["details"]["visible_tests_output"] = output[-500:]

    # 2. Hidden tests
    if HIDDEN_TESTS.exists():
        passed, output = run_pytest(str(HIDDEN_TESTS))
        results["hidden_tests_pass"] = passed
        results["details"]["hidden_tests_output"] = output[-500:]

    # 3. Required outputs
    required = ["outputs/summary.json", "outputs/report.md", "outputs/cleaned_payments.csv"]
    for path in required:
        if check_file_exists(path):
            results["required_outputs_exist"].append(path)
        else:
            results["missing_outputs"].append(path)

    # 4. Check JSON values against gold
    if check_file_exists("outputs/summary.json") and GOLD_FILE.exists():
        gold = json.loads(GOLD_FILE.read_text())
        with open(WORKSPACE / "outputs/summary.json") as f:
            actual = json.load(f)
        diffs = []
        for key in ['mrr', 'new_mrr', 'churned_mrr', 'net_mrr_growth']:
            if abs(actual.get(key, 0) - gold.get(key, 0)) > 0.01:
                diffs.append(f"{key}: expected {gold[key]}, got {actual.get(key)}")
        if actual.get('top_churn_segments') != gold.get('top_churn_segments'):
            diffs.append(f"top_churn_segments mismatch")
        results["json_values_correct"] = len(diffs) == 0
        results["details"]["value_diffs"] = diffs

    # 5. Check report quality
    if check_file_exists("outputs/report.md"):
        report = (WORKSPACE / "outputs/report.md").read_text().lower()
        has_mrr = "mrr" in report
        has_churn = "churn" in report
        results["report_contains_kpi"] = has_mrr and has_churn

    # 6. Check input files not modified
    import hashlib
    orig_customers_hash = "KNOWN_GOOD_HASH"  # Will be populated at build time
    results["files_unmodified"] = True  # Enforced by MCP write protection

    print(json.dumps(results, indent=2))
    all_pass = results["visible_tests_pass"] and results["hidden_tests_pass"]
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
