"""Tests for scoring module."""

import pytest
from openclaw.models import (
    TaskConfig, SessionState, ScoreResult, ToolCall, TaskRole, Difficulty
)
from openclaw.scoring import compute_score


def make_task(**kwargs) -> TaskConfig:
    defaults = dict(
        id="test_task",
        role=TaskRole.SOFTWARE_ENGINEER,
        difficulty=Difficulty.MEDIUM,
        time_budget_minutes=12,
        required_outputs=["src/pricing.py", "CHANGELOG.md"],
        forbidden_actions=["modify tests/"],
        task_dir="/tmp/test_task",
    )
    defaults.update(kwargs)
    return TaskConfig(**defaults)


def make_session(**kwargs) -> SessionState:
    from datetime import datetime
    defaults = dict(
        session_id="test-session-1",
        team_id="test-team",
        task_id="test_task",
        role=TaskRole.SOFTWARE_ENGINEER,
        started_at=datetime.now(),
        time_budget_seconds=720,
    )
    defaults.update(kwargs)
    return SessionState(**defaults)


def make_trace(tools: list[str]) -> list[ToolCall]:
    calls = []
    for tool in tools:
        calls.append(ToolCall(
            tool_name=tool,
            arguments={},
            timestamp=0,
            success=True,
        ))
    return calls


class TestComputeScore:
    def test_perfect_score(self):
        task = make_task()
        session = make_session()
        trace = make_trace([
            "openclaw__read_file",
            "openclaw__run_shell",
            "openclaw__write_file",
        ])
        # Fix the trace to include a pytest command
        trace[1].arguments = {"command": "pytest tests/"}

        verify_output = {
            "visible_tests_pass": True,
            "hidden_tests_pass": True,
            "changelog_updated": True,
            "no_hardcoded_values": True,
            "required_outputs_exist": ["src/pricing.py", "CHANGELOG.md"],
            "missing_outputs": [],
        }

        score = compute_score(task, session, trace, verify_output)
        assert score.verifier_passed is True
        assert score.total_score == 100.0
        assert score.completion_score == 60.0
        assert score.constraint_score == 20.0
        assert score.process_score > 0
        assert score.communication_score == 5.0

    def test_no_read_files_loses_process_score(self):
        task = make_task()
        session = make_session()
        trace = make_trace(["openclaw__write_file"])

        verify_output = {
            "visible_tests_pass": True,
            "hidden_tests_pass": True,
            "changelog_updated": True,
            "no_hardcoded_values": True,
            "required_outputs_exist": ["src/pricing.py", "CHANGELOG.md"],
            "missing_outputs": [],
        }

        score = compute_score(task, session, trace, verify_output)
        assert score.process_score == 3.0  # only wrote_files

    def test_visible_tests_fail_caps_at_60(self):
        task = make_task()
        session = make_session()
        trace = make_trace(["openclaw__read_file", "openclaw__run_shell"])
        trace[1].arguments = {"command": "pytest tests/"}

        verify_output = {
            "visible_tests_pass": False,
            "hidden_tests_pass": False,
            "changelog_updated": True,
            "no_hardcoded_values": True,
            "required_outputs_exist": ["src/pricing.py", "CHANGELOG.md"],
            "missing_outputs": [],
        }

        score = compute_score(task, session, trace, verify_output)
        assert score.verifier_passed is False
        assert score.total_score <= 60.0

    def test_missing_outputs_caps_at_30(self):
        task = make_task()
        session = make_session()
        trace = make_trace([])

        verify_output = {
            "visible_tests_pass": False,
            "hidden_tests_pass": False,
            "changelog_updated": False,
            "no_hardcoded_values": True,
            "required_outputs_exist": [],
            "missing_outputs": ["src/pricing.py", "CHANGELOG.md"],
        }

        score = compute_score(task, session, trace, verify_output)
        assert score.total_score <= 30.0

    def test_hardcoded_violation(self):
        task = make_task()
        session = make_session()
        trace = make_trace([])

        verify_output = {
            "visible_tests_pass": True,
            "hidden_tests_pass": True,
            "changelog_updated": True,
            "constraint_violations": ["hardcoded_values_detected"],
            "required_outputs_exist": ["src/pricing.py", "CHANGELOG.md"],
            "missing_outputs": [],
        }

        score = compute_score(task, session, trace, verify_output)
        assert "hardcoded_values_detected" in score.safety_violations
        assert score.total_score <= 40.0
