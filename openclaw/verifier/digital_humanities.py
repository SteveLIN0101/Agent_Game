"""Core-06 Digital Humanities verifier.

Checks: metadata accuracy, entity normalization, date format,
timeline ordering, evidence citations, OCR correction quality.
"""

from ..models import SessionState
from .base import AbstractVerifier, CompletionResult, ConstraintResult


class DigitalHumanitiesVerifier(AbstractVerifier):
    """Verifier for digital humanities tasks (Core-06)."""

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
            "cd /workspace && python3 -m pytest /opt/verifier/hidden_tests/ -v --tb=short 2>&1"
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

        stdout, _, _ = self._exec(
            session, "head -1 /workspace/output/metadata.csv"
        )
        required_cols = ["doc_id", "sender", "recipient", "date", "place"]
        for col in required_cols:
            if col not in stdout:
                violations.append(f"metadata_missing_column: {col}")

        stdout, _, _ = self._exec(
            session, "cat /workspace/output/metadata.csv"
        )
        if "unknown" not in stdout.lower():
            violations.append("no_unknown_values_for_uncertain_fields")

        return ConstraintResult(
            passed=len(violations) == 0,
            score=score if not violations else 0.0,
            violations=violations,
        )

    def _exec(self, session: SessionState, command: str) -> tuple:
        raise NotImplementedError("Patch _exec with session_manager.exec_command")
