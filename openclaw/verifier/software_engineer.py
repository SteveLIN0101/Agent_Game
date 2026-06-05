"""Core-01 Software Engineer verifier.

Checks: visible pytest, hidden pytest, CHANGELOG update, no hardcoded values,
tests/ unmodified, required files exist.
"""

from ..models import SessionState, TaskConfig
from .base import AbstractVerifier, CompletionResult, ConstraintResult


class SoftwareEngineerVerifier(AbstractVerifier):
    """Verifier for software engineering tasks (Core-01)."""

    async def check_completion(self, session: SessionState) -> CompletionResult:
        """Run visible + hidden tests, check outputs."""
        details = {}
        score = 0.0
        failed = []

        # Run visible tests
        stdout, stderr, exit_code = self._exec(
            session, "cd /workspace && pytest tests/ -v --tb=short 2>&1"
        )
        visible_pass = exit_code == 0
        details["visible_tests_pass"] = visible_pass
        details["visible_tests_output"] = (stdout + stderr)[-1000:]
        if visible_pass:
            score += 40.0
        else:
            failed.append("visible_tests")

        # Run hidden tests
        stdout, stderr, exit_code = self._exec(
            session, "cd /workspace && pytest /opt/verifier/hidden_tests/ -v --tb=short 2>&1"
        )
        hidden_pass = exit_code == 0
        details["hidden_tests_pass"] = hidden_pass
        details["hidden_tests_output"] = (stdout + stderr)[-1000:]
        if hidden_pass:
            score += 20.0
        else:
            failed.append("hidden_tests")

        # Check required outputs exist
        outputs = self._check_required_outputs(session)
        details["required_outputs"] = outputs

        details["failed"] = failed
        return CompletionResult(
            passed=visible_pass and hidden_pass and not outputs["missing"],
            score=score,
            details=details,
        )

    async def check_constraints(self, session: SessionState) -> ConstraintResult:
        """Check no hardcoding, CHANGELOG updated."""
        violations = []
        score = 10.0  # Base: tests not modified (enforced at MCP level)

        # Check for hardcoded values in pricing.py
        stdout, _, _ = self._exec(
            session, "cat /workspace/src/pricing.py"
        )
        if "100" in stdout and "15" in stdout and "75" in stdout:
            # Suspicious if all hidden test values appear
            violations.append("possible_hardcoded_test_values")
        else:
            score += 10.0

        # Check CHANGELOG
        stdout, _, _ = self._exec(
            session, "cat /workspace/CHANGELOG.md"
        )
        content_lower = stdout.lower()
        if "discount" not in content_lower and "coupon" not in content_lower:
            violations.append("changelog_missing_fix_description")

        return ConstraintResult(
            passed=len(violations) == 0,
            score=score,
            violations=violations,
        )

    def _exec(self, session: SessionState, command: str) -> tuple[str, str, int]:
        """Execute command in container — to be patched by server."""
        raise NotImplementedError("Patch _exec with session_manager.exec_command")
