"""Core-03 UI Designer: color_token_fix verify.py"""
import json
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path("/workspace")
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
        "design_token_compliance": False,
        "hardcoded_colors_removed": False,
        "changelog_updated": True,
        "no_hardcoded_values": True,
        "design_notes_complete": False,
        "tests_unmodified": True,
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
    required = ["styles/theme.css", "design_notes.md"]
    for path in required:
        if check_file_exists(path):
            results["required_outputs_exist"].append(path)
        else:
            results["missing_outputs"].append(path)

    # 4. Check design token compliance
    if check_file_exists("styles/theme.css"):
        css = (WORKSPACE / "styles/theme.css").read_text()
        import re
        # Remove :root block for checking
        css_no_root = re.sub(r':root\s*\{[^}]*\}', '', css, flags=re.DOTALL)
        has_hex = bool(re.search(r'(?<!var\(--)#[0-9a-fA-F]{3,6}', css_no_root))
        has_rgb = 'rgb(' in css_no_root or 'rgba(' in css_no_root
        results["hardcoded_colors_removed"] = not has_hex and not has_rgb
        results["design_token_compliance"] = 'var(--' in css

    # 5. Check design notes
    if check_file_exists("design_notes.md"):
        notes = (WORKSPACE / "design_notes.md").read_text()
        results["design_notes_complete"] = len(notes.strip()) > 0

    print(json.dumps(results, indent=2))
    all_pass = results["visible_tests_pass"] and results["hidden_tests_pass"]
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
