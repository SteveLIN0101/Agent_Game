"""Core-05 Localization: basic_translate verify.py"""
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
        "visible_tests_pass": False,
        "hidden_tests_pass": False,
        "required_outputs_exist": [],
        "missing_outputs": [],
        "key_integrity": False,
        "placeholder_preserved": False,
        "glossary_compliance": False,
        "qa_report_complete": False,
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

    required = ["output/strings_zh.json", "output/localization_qa.json"]
    for path in required:
        if (WORKSPACE / path).exists():
            results["required_outputs_exist"].append(path)
        else:
            results["missing_outputs"].append(path)

    # Check key integrity
    if (WORKSPACE / "output/strings_zh.json").exists() and (WORKSPACE / "source/strings_en.json").exists():
        src = json.loads((WORKSPACE / "source/strings_en.json").read_text())
        tgt = json.loads((WORKSPACE / "output/strings_zh.json").read_text())
        results["key_integrity"] = set(src.keys()) == set(tgt.keys())

    # Check glossary
    if (WORKSPACE / "output/strings_zh.json").exists():
        text = json.dumps(json.loads((WORKSPACE / "output/strings_zh.json").read_text()), ensure_ascii=False)
        results["glossary_compliance"] = '空间站' not in text and '开票系统' not in text and '模版' not in text

    # Check QA report
    if (WORKSPACE / "output/localization_qa.json").exists():
        qa = json.loads((WORKSPACE / "output/localization_qa.json").read_text())
        results["qa_report_complete"] = len(qa) > 0

    print(json.dumps(results, indent=2))
    all_pass = results["visible_tests_pass"] and results["hidden_tests_pass"]
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
