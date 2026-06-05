"""Tests for budget enforcement and shell whitelist."""

import pytest
from openclaw.budget import (
    validate_shell_command,
    validate_read_path,
    validate_write_path,
    check_budget,
    BudgetExceededError,
    ForbiddenCommandError,
    ForbiddenPathError,
)


class TestShellWhitelist:
    def test_allows_pytest(self):
        assert validate_shell_command("pytest tests/") is True

    def test_allows_python(self):
        assert validate_shell_command("python -c 'print(1)'") is True
        assert validate_shell_command("python3 script.py") is True

    def test_allows_ls_cat_grep(self):
        assert validate_shell_command("ls -la") is True
        assert validate_shell_command("cat file.txt") is True
        assert validate_shell_command("grep -r pattern .") is True

    def test_allows_git(self):
        assert validate_shell_command("git diff") is True
        assert validate_shell_command("git status") is True

    def test_rejects_rm(self):
        with pytest.raises(ForbiddenCommandError, match="forbidden"):
            validate_shell_command("rm -rf file.txt")

    def test_rejects_curl(self):
        with pytest.raises(ForbiddenCommandError, match="forbidden"):
            validate_shell_command("curl http://example.com")

    def test_rejects_pip_install(self):
        with pytest.raises(ForbiddenCommandError, match="forbidden"):
            validate_shell_command("pip install requests")

    def test_rejects_unknown_command(self):
        with pytest.raises(ForbiddenCommandError, match="whitelist"):
            validate_shell_command("vim file.txt")

    def test_rejects_hidden_evaluator_paths(self):
        with pytest.raises(ForbiddenCommandError, match="hidden evaluator"):
            validate_shell_command("cat /opt/verifier/hidden_tests/test_hidden.py")
        with pytest.raises(ForbiddenCommandError, match="hidden evaluator"):
            validate_shell_command("find /opt -type f")
        with pytest.raises(ForbiddenCommandError, match="hidden evaluator"):
            validate_shell_command("cat expected/gold.json")


class TestReadPathProtection:
    def test_allows_visible_tests_and_sources(self):
        assert validate_read_path("tests/test_pricing.py") is True
        assert validate_read_path("src/pricing.py") is True

    def test_rejects_expected_and_verifier_paths(self):
        with pytest.raises(ForbiddenPathError, match="hidden"):
            validate_read_path("expected/gold.json")
        with pytest.raises(ForbiddenPathError, match="hidden"):
            validate_read_path("/opt/verifier/hidden_tests/test_hidden.py")


class TestWritePathProtection:
    def test_allows_src_dir(self):
        assert validate_write_path("src/pricing.py") is True
        assert validate_write_path("./src/module.py") is True
        assert validate_write_path("CHANGELOG.md") is True

    def test_rejects_tests_dir(self):
        with pytest.raises(ForbiddenPathError, match="read-only"):
            validate_write_path("tests/test_pricing.py")
        with pytest.raises(ForbiddenPathError, match="read-only"):
            validate_write_path("./tests/test_file.py")

    def test_rejects_expected_dir(self):
        with pytest.raises(ForbiddenPathError, match="read-only"):
            validate_write_path("expected/gold.json")

    def test_rejects_opt_verifier(self):
        with pytest.raises(ForbiddenPathError, match="read-only"):
            validate_write_path("/opt/verifier/test.py")


class TestBudget:
    def test_within_budget(self):
        assert check_budget(100, 720) is True

    def test_exceeded_budget(self):
        with pytest.raises(BudgetExceededError, match="exceeded"):
            check_budget(800, 720)

    def test_exact_budget_edge(self):
        assert check_budget(720, 720) is True
