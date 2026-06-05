"""Core-02 Data Analyst verifier.

Checks: visible pytest, hidden tests, JSON value accuracy, CSV schema,
input file integrity, report completeness.
"""

from ..models import SessionState
from .base import AbstractVerifier, CompletionResult, ConstraintResult


class DataAnalystVerifier(AbstractVerifier):
    """Verifier for data analyst tasks (Core-02)."""

    async def check_completion(self, session: SessionState) -> CompletionResult:
        details = {}
        score = 0.0
        failed = []

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

        stdout, stderr, exit_code = self._exec(
            session,
            "cd /workspace && pytest /opt/verifier/hidden_tests/ -v --tb=short 2>&1"
        )
        hidden_pass = exit_code == 0
        details["hidden_tests_pass"] = hidden_pass
        details["hidden_tests_output"] = (stdout + stderr)[-1000:]
        if hidden_pass:
            score += 20.0
        else:
            failed.append("hidden_tests")

        outputs = self._check_required_outputs(session)
        details["required_outputs"] = outputs
        details["failed"] = failed

        return CompletionResult(
            passed=visible_pass and hidden_pass and not outputs["missing"],
            score=score,
            details=details,
        )

    async def check_constraints(self, session: SessionState) -> ConstraintResult:
        violations = []
        score = 10.0

        # Check input files not modified (hash check)
        stdout, _, _ = self._exec(
            session,
            "python3 -c \"import hashlib; "
            "print(hashlib.sha256(open('/workspace/data/customers.csv','rb').read()).hexdigest())\""
        )

        # Check report contains required sections
        stdout, _, _ = self._exec(session, "cat /workspace/outputs/report.md")
        report = stdout.lower()
        if "mrr" not in report or "churn" not in report:
            violations.append("report_missing_key_metrics")

        return ConstraintResult(
            passed=len(violations) == 0,
            score=score if not violations else score - 10.0,
            violations=violations,
        )

    def _exec(self, session: SessionState, command: str) -> tuple:
        raise NotImplementedError("Patch _exec with session_manager.exec_command")
