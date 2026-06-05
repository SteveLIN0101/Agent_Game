"""Tests for the agent-skill utility pilot plumbing."""

import json
from datetime import datetime

import pytest

from openclaw import mcp_server
from openclaw.models import (
    Difficulty,
    ScoreResult,
    SessionState,
    TaskConfig,
    TaskRole,
)
from openclaw.trace import TraceCollector
from scripts import analyze_skill_utility as analyzer


def make_session(**kwargs) -> SessionState:
    defaults = dict(
        session_id="pilot-session",
        team_id="team",
        task_id="pilot_task",
        role=TaskRole.SOFTWARE_ENGINEER,
        started_at=datetime.now(),
    )
    defaults.update(kwargs)
    return SessionState(**defaults)


def make_score(**kwargs) -> ScoreResult:
    defaults = dict(
        task_id="pilot_task",
        role="software_engineer",
        total_score=88.0,
        completion_score=60.0,
        constraint_score=20.0,
        process_score=8.0,
        communication_score=0.0,
        verifier_passed=True,
        time_seconds=12,
        tool_calls=3,
        trace_summary={"tools_used": ["openclaw__read_file"]},
    )
    defaults.update(kwargs)
    return ScoreResult(**defaults)


def test_session_and_score_pilot_defaults_are_backward_compatible():
    session = make_session()
    score = make_score()

    assert session.skill_variant == "control"
    assert session.pilot_run_id == ""
    assert session.trial_index == 0
    assert score.pilot_metadata == {}


@pytest.mark.asyncio
async def test_get_task_accepts_and_returns_pilot_metadata(monkeypatch):
    task = TaskConfig(
        id="pilot_task",
        role=TaskRole.SOFTWARE_ENGINEER,
        difficulty=Difficulty.EASY,
        time_budget_minutes=6,
        required_outputs=["outputs/result.json"],
    )
    session = make_session(time_budget_seconds=360)

    class FakeRegistry:
        def get(self, task_id):
            assert task_id == "pilot_task"
            return task

        def get_instructions(self, task_config):
            assert task_config is task
            return "Do the pilot task."

        def list_input_files(self, task_config):
            assert task_config is task
            return ["issue.md"]

    class FakeSessionManager:
        def create_session(self, team_id, task_config):
            assert team_id == "dev-team"
            assert task_config is task
            return session

    monkeypatch.setattr(mcp_server, "_get_registry", lambda: FakeRegistry())
    monkeypatch.setattr(mcp_server, "_get_session_mgr", lambda: FakeSessionManager())

    try:
        raw = await mcp_server.openclaw__get_task(
            task_id="pilot_task",
            pilot_run_id="pilot-001",
            agent_id="codex",
            model_id="gpt-5",
            skill_variant="skill",
            trial_index=2,
            seed="20260527",
        )
        result = json.loads(raw)
        metadata = result["pilot_metadata"]
        assert metadata["pilot_run_id"] == "pilot-001"
        assert metadata["agent_id"] == "codex"
        assert metadata["model_id"] == "gpt-5"
        assert metadata["skill_variant"] == "skill"
        assert metadata["trial_index"] == 2
        assert metadata["seed"] == "20260527"
        assert mcp_server._sessions[session.session_id].skill_variant == "skill"
    finally:
        mcp_server._sessions.pop(session.session_id, None)
        mcp_server._traces.pop(session.session_id, None)


def test_trace_summary_records_duration_exit_codes_and_failures():
    trace = TraceCollector()
    trace.record(
        "openclaw__run_shell",
        {"command": "pytest tests/", "exit_code": 1},
        duration_ms=12.5,
    )
    trace.record("openclaw__read_file", {"path": "issue.md"}, duration_ms=3.0)
    trace.record(
        "openclaw__write_file",
        {"path": "tests/test_x.py"},
        success=False,
        error="forbidden",
        duration_ms=1.0,
    )

    summary = trace.summary()
    assert summary["total_calls"] == 3
    assert summary["shell_exit_codes"] == [1]
    assert summary["failed_shell_commands"] == ["pytest tests/"]
    assert summary["failed_calls"][0]["tool_name"] == "openclaw__write_file"
    assert summary["total_duration_ms"] == 16.5


def test_append_pilot_result_writes_jsonl(monkeypatch, tmp_path):
    session = make_session(
        pilot_run_id="pilot-001",
        agent_id="codex",
        model_id="gpt-5",
        skill_variant="skill",
    )
    score = make_score(
        pilot_metadata=mcp_server._session_pilot_metadata(session),
        trace_summary={"tools_used": [], "failure_tags": ["F5_hidden_failure"]},
    )
    monkeypatch.setattr(mcp_server, "PROJECT_ROOT", tmp_path)

    mcp_server._append_pilot_result(
        session=session,
        score=score,
        verify_output={"visible_tests_pass": True, "hidden_tests_pass": False},
        verifier_exit_code=0,
        failure_tags=["F5_hidden_failure"],
    )

    path = tmp_path / "runs" / "pilot_results.jsonl"
    record = json.loads(path.read_text(encoding="utf-8").strip())
    assert record["task_id"] == "pilot_task"
    assert record["condition"] == "skill"
    assert record["pass"] is True
    assert record["pilot_metadata"]["pilot_run_id"] == "pilot-001"
    assert record["failure_tags"] == ["F5_hidden_failure"]


def test_analyzer_computes_paired_wtl_and_reliability(tmp_path):
    records = [
        {
            "task_id": "task_a",
            "role": "software_engineer",
            "condition": "control",
            "pilot_metadata": {"pilot_run_id": "p", "trial_index": 0},
            "score": {"total_score": 50, "verifier_passed": False},
            "pass": False,
            "elapsed_seconds": 10,
            "failure_tags": ["F6_visible_failure"],
        },
        {
            "task_id": "task_a",
            "role": "software_engineer",
            "condition": "skill",
            "pilot_metadata": {"pilot_run_id": "p", "trial_index": 0},
            "score": {"total_score": 90, "verifier_passed": True},
            "pass": True,
            "elapsed_seconds": 20,
        },
        {
            "task_id": "task_b",
            "role": "data_analyst",
            "condition": "control",
            "pilot_metadata": {"pilot_run_id": "p", "trial_index": 0},
            "score": {"total_score": 80, "verifier_passed": True},
            "pass": True,
            "elapsed_seconds": 10,
        },
        {
            "task_id": "task_b",
            "role": "data_analyst",
            "condition": "skill",
            "pilot_metadata": {"pilot_run_id": "p", "trial_index": 0},
            "score": {"total_score": 70, "verifier_passed": True},
            "pass": True,
            "elapsed_seconds": 15,
            "failure_tags": ["F3_tool_process"],
        },
        {
            "task_id": "task_a",
            "role": "software_engineer",
            "condition": "control",
            "pilot_metadata": {"pilot_run_id": "p", "trial_index": 1},
            "score": {"total_score": 60, "verifier_passed": True},
            "pass": True,
        },
        {
            "task_id": "task_a",
            "role": "software_engineer",
            "condition": "skill",
            "pilot_metadata": {"pilot_run_id": "p", "trial_index": 1},
            "score": {"total_score": 90, "verifier_passed": True},
            "pass": True,
        },
    ]
    path = tmp_path / "pilot_results.jsonl"
    path.write_text(
        "\n".join(json.dumps(r) for r in records) + "\n",
        encoding="utf-8",
    )

    loaded = analyzer.load_jsonl(path)
    pairs, incomplete = analyzer.build_main_pairs(loaded)
    summary = analyzer.summarize_pairs(pairs, bootstrap_n=100)
    reliability = analyzer.summarize_reliability(loaded)
    failures = analyzer.summarize_failures(loaded)

    assert incomplete == []
    assert summary["n_pairs"] == 2
    assert summary["wins"] == 1
    assert summary["losses"] == 1
    assert summary["delta_pass_at_1"] == 0.5
    assert reliability["n_tasks"] == 1
    assert reliability["delta_pass_k_rate"] == 0.5
    assert failures["control"]["F6_visible_failure"] == 1
    assert failures["skill"]["F3_tool_process"] == 1


def test_analyzer_filters_by_pilot_run_id():
    records = [
        {"task_id": "a", "pilot_metadata": {"pilot_run_id": "keep"}},
        {"task_id": "b", "pilot_metadata": {"pilot_run_id": "drop"}},
        {"task_id": "c", "pilot_metadata": {}},
    ]

    assert analyzer.filter_records(records, pilot_run_id="keep") == [records[0]]
    assert analyzer.filter_records(records, pilot_run_id="") == records
