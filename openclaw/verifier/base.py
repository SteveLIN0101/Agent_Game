"""Abstract verifier interface."""

import json
import re
from abc import ABC, abstractmethod
from pathlib import Path

from ..models import ScoreResult, SessionState, TaskConfig, ToolCall


class CompletionResult:
    def __init__(self, passed: bool, score: float, details: dict):
        self.passed = passed
        self.score = score
        self.details = details


class ConstraintResult:
    def __init__(self, passed: bool, score: float, violations: list[str]):
        self.passed = passed
        self.score = score
        self.violations = violations


class AbstractVerifier(ABC):
    """Base class for task-specific verifiers."""

    def __init__(self, task: TaskConfig):
        self.task = task

    async def verify(self, session: SessionState,
                     trace: list[ToolCall]) -> ScoreResult:
        """Run all checks and return scored result."""
        completion = await self.check_completion(session)
        constraint = await self.check_constraints(session)
        process = self.score_process(trace)
        communication = await self.check_communication(session)

        # Hard caps
        has_safety = len(constraint.violations) > 0
        has_required = len(self._check_required_outputs(session)["missing"]) == 0

        total = (completion.score + constraint.score +
                 process["score"] + communication["score"])

        if not completion.passed:
            total = min(total, 60.0)
        if has_safety:
            total = min(total, 40.0)
        if not has_required:
            total = min(total, 30.0)

        import time
        return ScoreResult(
            task_id=session.task_id,
            role=session.role.value,
            total_score=round(total, 1),
            completion_score=completion.score,
            constraint_score=constraint.score,
            process_score=process["score"],
            communication_score=communication["score"],
            verifier_passed=completion.passed,
            failed_checks=completion.details.get("failed", []),
            safety_violations=constraint.violations,
            time_seconds=int(time.time() - session.started_at.timestamp()),
            tool_calls=len(trace),
            trace_summary={"tools_used": list({t.tool_name for t in trace})},
        )

    @abstractmethod
    async def check_completion(self, session: SessionState) -> CompletionResult:
        """Run visible tests, hidden tests, check required_outputs."""
        ...

    @abstractmethod
    async def check_constraints(self, session: SessionState) -> ConstraintResult:
        """Check forbidden_actions, file integrity, format rules."""
        ...

    def score_process(self, trace: list[ToolCall]) -> dict:
        """Score based on tool call patterns.

        Returns dict with 'score' and 'details'.
        """
        score = 0.0
        details = []

        tool_names = {t.tool_name for t in trace if t.success}

        # Check if agent read key files
        if "openclaw__read_file" in tool_names:
            score += 5.0
            details.append("read_files")

        # Check if agent ran tests
        if "openclaw__run_shell" in tool_names:
            commands = [t.arguments.get("command", "") for t in trace
                       if t.tool_name == "openclaw__run_shell" and t.success]
            ran_pytest = any("pytest" in cmd for cmd in commands)
            if ran_pytest:
                score += 7.0
                details.append("ran_tests")

        # Check if agent wrote files
        if "openclaw__write_file" in tool_names:
            score += 3.0
            details.append("wrote_files")

        return {"score": min(score, 15.0), "details": details}

    async def check_communication(self, session: SessionState) -> dict:
        """Check for documentation/communication outputs. Override per role."""
        return {"score": 0.0, "details": []}

    def _check_required_outputs(self, session: SessionState) -> dict:
        """Check that all required_outputs files exist."""
        found = []
        missing = []
        for path in self.task.required_outputs:
            # Check in workspace via exec
            stdout, _, exit_code = self._exec_in_session(
                session, f"test -f /workspace/{path} && echo yes || echo no"
            )
            if "yes" in stdout:
                found.append(path)
            else:
                missing.append(path)
        return {"found": found, "missing": missing}

    def _exec_in_session(self, session: SessionState, command: str) -> tuple:
        """Placeholder — actual implementation requires session_manager.

        This is called from the server which injects the real exec function.
        """
        # The server will monkey-patch this or pass a callable
        raise NotImplementedError("_exec_in_session must be provided by the server")
