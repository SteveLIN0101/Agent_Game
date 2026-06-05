"""OpenClaw MCP Server — exposes occupational benchmark tools to agents.

Usage:
    python -m openclaw.mcp_server
    # or:
    openclaw-server
"""

import json
import time
from pathlib import Path

from mcp.server import FastMCP
from mcp.server.auth.settings import AuthSettings

from .auth import token_verifier
from .config import PROJECT_ROOT, AUTH_TOKEN
from .models import SessionState
from .task_registry import TaskRegistry
from .session_manager import SessionManager
from .budget import (
    validate_shell_command,
    validate_read_path,
    validate_write_path,
    check_budget,
    BudgetExceededError,
    ForbiddenCommandError,
    ForbiddenPathError,
)
from .trace import TraceCollector
from .scoring import compute_score

# Initialize FastMCP server
# Enable auth only when explicitly configured (requires OAuth infrastructure)
_auth_kwargs = {}
if AUTH_TOKEN != "openclaw-dev-token":
    import os
    issuer = os.getenv("OPENCLAW_OAUTH_ISSUER", "http://localhost:8000/oauth")
    resource = os.getenv("OPENCLAW_OAUTH_RESOURCE", "http://localhost:8000")
    _auth_kwargs = dict(
        token_verifier=token_verifier,
        auth=AuthSettings(
            issuer_url=issuer,
            resource_server_url=resource,
            required_scopes=["openclaw:task"],
        ),
    )

mcp = FastMCP(
    name="OpenClaw Occupational Core-6",
    instructions="MCP-based agent benchmark for six occupational roles",
    **_auth_kwargs,
)

# Global state (in production, use a database)
_sessions: dict[str, SessionState] = {}  # task_session_id -> SessionState
_traces: dict[str, TraceCollector] = {}  # task_session_id -> TraceCollector

# Lazy-initialized singletons
_registry: TaskRegistry | None = None
_session_mgr: SessionManager | None = None


def _get_registry() -> TaskRegistry:
    global _registry
    if _registry is None:
        _registry = TaskRegistry()
    return _registry


def _get_session_mgr() -> SessionManager:
    global _session_mgr
    if _session_mgr is None:
        _session_mgr = SessionManager(PROJECT_ROOT / "tasks")
    return _session_mgr


# ── MCP Tools ────────────────────────────────────────────────────────────


@mcp.tool()
async def openclaw__get_task(
    task_id: str = "",
    role: str = "",
    pilot_run_id: str = "",
    agent_id: str = "",
    model_id: str = "",
    skill_variant: str = "control",
    trial_index: int = 0,
    seed: str = "",
) -> str:
    """Start a new task. Returns instructions and workspace info.

    Call this first. If task_id is empty, a random task is assigned.
    Use role to filter by occupation (software_engineer, data_analyst, etc.).

    Args:
        task_id: Optional specific task ID to request
        role: Optional role filter if task_id is not specified
        pilot_run_id: Optional experiment/run identifier for paired pilots
        agent_id: Optional agent or harness identifier
        model_id: Optional model identifier
        skill_variant: Optional condition label, e.g. control or skill
        trial_index: Optional repeated-run index
        seed: Optional randomization seed

    Returns:
        JSON with instructions, workspace_path, files list, time_budget,
        and a task_session_id you must pass to all subsequent tool calls.
    """
    registry = _get_registry()
    session_mgr = _get_session_mgr()

    # Select task
    if task_id:
        task = registry.get(task_id)
    elif role:
        task = registry.get_random(role=role)
    else:
        task = registry.get_random()

    instructions = registry.get_instructions(task)
    files = registry.list_input_files(task)

    # Create session and Docker container
    team_id = "dev-team"  # In production, from auth
    session = session_mgr.create_session(team_id, task)
    session.pilot_run_id = pilot_run_id
    session.agent_id = agent_id
    session.model_id = model_id
    session.skill_variant = skill_variant or "control"
    session.trial_index = trial_index
    session.seed = seed

    # Store session
    _sessions[session.session_id] = session
    _traces[session.session_id] = TraceCollector()

    result = {
        "task_session_id": session.session_id,
        "task_id": task.id,
        "role": task.role.value,
        "difficulty": task.difficulty.value,
        "time_budget_seconds": session.time_budget_seconds,
        "workspace_path": session.workspace_path,
        "instructions": instructions,
        "files": files,
        "required_outputs": task.required_outputs,
        "pilot_metadata": _session_pilot_metadata(session),
        "hint": (
            "All subsequent tool calls require the task_session_id above. "
            "Typical workflow: list_workspace → read_file (issue + src) "
            "→ run_shell (pytest) → write_file (fix) → run_shell (verify) "
            "→ submit. The server auto-runs tests on submit."
        ),
    }

    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool()
async def openclaw__list_workspace(
    task_session_id: str,
    path: str = ".",
) -> str:
    """List files and directories in the workspace.

    Args:
        task_session_id: Task session ID from get_task
        path: Directory path relative to workspace root (default: ".")

    Returns:
        JSON with entries list
    """
    _check_session(task_session_id)
    session_mgr = _get_session_mgr()
    session = _sessions[task_session_id]
    started = time.perf_counter()

    try:
        validate_read_path(path)
        entries = session_mgr.list_dir(session, path)
        _record_tool(
            task_session_id,
            "openclaw__list_workspace",
            {"path": path},
            duration_ms=_duration_ms(started),
        )
        return json.dumps({"path": path, "entries": entries}, indent=2)
    except Exception as e:
        _record_tool(
            task_session_id,
            "openclaw__list_workspace",
            {"path": path},
            success=False,
            error=str(e),
            duration_ms=_duration_ms(started),
        )
        return json.dumps({"error": str(e)})


@mcp.tool()
async def openclaw__read_file(
    task_session_id: str,
    path: str,
) -> str:
    """Read a file from the workspace.

    Args:
        task_session_id: Task session ID from get_task
        path: File path relative to workspace root

    Returns:
        File contents as text
    """
    _check_session(task_session_id)

    session_mgr = _get_session_mgr()
    session = _sessions[task_session_id]
    started = time.perf_counter()

    try:
        validate_read_path(path)
        content = session_mgr.read_file(session, path)
        _record_tool(
            task_session_id,
            "openclaw__read_file",
            {"path": path},
            duration_ms=_duration_ms(started),
        )
        return json.dumps({
            "path": path,
            "content": content,
            "line_count": len(content.split("\n")),
        }, indent=2, ensure_ascii=False)
    except Exception as e:
        _record_tool(task_session_id, "openclaw__read_file",
                     {"path": path}, success=False, error=str(e),
                     duration_ms=_duration_ms(started))
        return json.dumps({"error": str(e)})


@mcp.tool()
async def openclaw__write_file(
    task_session_id: str,
    path: str,
    content: str,
) -> str:
    """Write content to a file in the workspace. Creates or overwrites.

    Cannot write to tests/, expected/, or /opt/verifier/ paths.

    Args:
        task_session_id: Task session ID from get_task
        path: File path relative to workspace root
        content: File content as string

    Returns:
        JSON with success status and bytes written
    """
    _check_session(task_session_id)
    started = time.perf_counter()

    try:
        validate_write_path(path)
    except ForbiddenPathError as e:
        _record_tool(
            task_session_id,
            "openclaw__write_file",
            {"path": path},
            success=False,
            error=str(e),
            duration_ms=_duration_ms(started),
        )
        return json.dumps({"error": str(e), "success": False})

    session_mgr = _get_session_mgr()
    session = _sessions[task_session_id]

    try:
        bytes_written = session_mgr.write_file(session, path, content)
        _record_tool(
            task_session_id,
            "openclaw__write_file",
            {"path": path, "bytes_written": bytes_written},
            duration_ms=_duration_ms(started),
        )
        return json.dumps({
            "success": True,
            "path": path,
            "bytes_written": bytes_written,
        }, indent=2)
    except Exception as e:
        _record_tool(task_session_id, "openclaw__write_file",
                     {"path": path}, success=False, error=str(e),
                     duration_ms=_duration_ms(started))
        return json.dumps({"error": str(e), "success": False})


@mcp.tool()
async def openclaw__run_shell(
    task_session_id: str,
    command: str,
    workdir: str = "/workspace",
) -> str:
    """Run a shell command in the workspace container.

    Allowed commands include: pytest, python, python3, ls, cat, head, tail,
    wc, grep, find, git, diff, cd, pwd, mkdir, cp, mv, touch, sed, awk,
    echo, sort, uniq, cut, node, npm, npx, patch, tr.
    Forbidden: rm, curl, wget, pip install, and other destructive operations.
    Compound commands with && or ; are supported (each sub-command is checked).

    Args:
        task_session_id: Task session ID from get_task
        command: Shell command to execute
        workdir: Working directory (default: /workspace)

    Returns:
        JSON with stdout, stderr, exit_code
    """
    _check_session(task_session_id)
    started = time.perf_counter()

    try:
        validate_shell_command(command)
    except ForbiddenCommandError as e:
        _record_tool(
            task_session_id,
            "openclaw__run_shell",
            {"command": command, "workdir": workdir, "exit_code": -1},
            success=False,
            error=str(e),
            duration_ms=_duration_ms(started),
        )
        return json.dumps({
            "error": str(e),
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
        })

    session_mgr = _get_session_mgr()
    session = _sessions[task_session_id]

    try:
        stdout, stderr, exit_code = session_mgr.exec_command(
            session, command, workdir=workdir
        )
        _record_tool(
            task_session_id,
            "openclaw__run_shell",
            {"command": command, "workdir": workdir, "exit_code": exit_code},
            duration_ms=_duration_ms(started),
        )
        return json.dumps({
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code,
        }, indent=2)
    except Exception as e:
        _record_tool(task_session_id, "openclaw__run_shell",
                     {"command": command, "workdir": workdir, "exit_code": -1},
                     success=False, error=str(e),
                     duration_ms=_duration_ms(started))
        return json.dumps({
            "error": str(e),
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
        })


@mcp.tool()
async def openclaw__submit(
    task_session_id: str,
) -> str:
    """Submit your work for scoring. This ends the session.

    The server will auto-run visible tests + hidden tests + constraint checks.
    No need to run tests manually — the server verifies correctness.

    Returns score breakdown with test output details.

    Args:
        task_session_id: Task session ID from get_task

    Returns:
        JSON with total_score, completion_score, constraint_score,
        process_score, communication_score, visible_test_output,
        hidden_test_output, and full trace summary.
    """
    _check_session(task_session_id)
    session = _sessions[task_session_id]
    trace_collector = _traces.get(task_session_id)

    if session.submitted:
        return json.dumps({"error": "Already submitted"})

    session.submitted = True

    session_mgr = _get_session_mgr()

    # Run the verifier script inside the container
    verify_script = "/opt/verifier/verifier/verify.py"
    stdout, stderr, exit_code = session_mgr.exec_command(
        session, f"python {verify_script}"
    )

    # Parse verifier output
    try:
        verify_output = json.loads(stdout) if stdout else {}
    except json.JSONDecodeError:
        verify_output = {
            "error": "Failed to parse verifier output",
            "raw_stdout": stdout[-1000:],
            "raw_stderr": stderr[-1000:],
        }

    # Extract test outputs for transparency
    details = verify_output.get("details", {})
    visible_test_output = details.get("visible_tests_output", "")
    hidden_test_output = details.get("hidden_tests_output", "")

    # Compute score
    registry = _get_registry()
    task = registry.get(session.task_id)
    trace = trace_collector.calls if trace_collector else []

    score = compute_score(task, session, trace, verify_output)

    # Add verifier details to trace
    score.trace_summary["visible_test_output"] = visible_test_output[-500:]
    score.trace_summary["hidden_test_output"] = hidden_test_output[-500:]
    score.trace_summary["verifier_exit_code"] = exit_code
    if trace_collector:
        score.trace_summary.update(trace_collector.summary())
    score.pilot_metadata = _session_pilot_metadata(session)
    failure_tags = _classify_failure_tags(
        session=session,
        score=score,
        verify_output=verify_output,
        verifier_exit_code=exit_code,
    )
    score.trace_summary["failure_tags"] = failure_tags
    _append_pilot_result(
        session=session,
        score=score,
        verify_output=verify_output,
        verifier_exit_code=exit_code,
        failure_tags=failure_tags,
        task=task,
    )

    # Destroy the container
    try:
        session_mgr.destroy_session(session)
    except Exception:
        pass  # Don't fail the submit if cleanup fails

    return score.model_dump_json(indent=2)


@mcp.tool()
async def openclaw__get_score(
    task_session_id: str,
) -> str:
    """Get current progress summary without submitting.

    Args:
        task_session_id: Task session ID from get_task

    Returns:
        JSON with current progress information
    """
    _check_session(task_session_id)
    session = _sessions[task_session_id]
    trace_collector = _traces.get(task_session_id)

    elapsed = int(time.time() - session.started_at.timestamp())
    remaining = max(0, session.time_budget_seconds - elapsed)

    if trace_collector:
        summary = trace_collector.summary()
    else:
        summary = {}

    return json.dumps({
        "task_session_id": session.session_id,
        "task_id": session.task_id,
        "elapsed_seconds": elapsed,
        "remaining_seconds": remaining,
        "tool_calls": summary.get("total_calls", 0),
        "tools_used": summary.get("tools_used", []),
        "files_read": summary.get("files_read", []),
        "files_written": summary.get("files_written", []),
        "pilot_metadata": _session_pilot_metadata(session),
        "submitted": session.submitted,
    }, indent=2)


# ── Helpers ──────────────────────────────────────────────────────────────


def _check_session(task_session_id: str) -> None:
    """Validate session exists and time budget not exceeded."""
    if task_session_id not in _sessions:
        raise ValueError(
            f"Task session '{task_session_id}' not found. "
            "Call openclaw__get_task first to create one."
        )

    session = _sessions[task_session_id]
    elapsed = int(time.time() - session.started_at.timestamp())

    try:
        check_budget(elapsed, session.time_budget_seconds)
    except BudgetExceededError as e:
        raise ValueError(
            f"{e} Your session has expired. "
            "Call openclaw__submit() to get your score."
        )


def _record_tool(task_session_id: str, tool_name: str, arguments: dict,
                 success: bool = True, error: str | None = None,
                 duration_ms: float = 0.0) -> None:
    """Record a tool call in the trace."""
    if task_session_id in _traces:
        _traces[task_session_id].record(
            tool_name=tool_name,
            arguments=arguments,
            success=success,
            error=error,
            duration_ms=duration_ms,
        )


def _duration_ms(started: float) -> float:
    """Return elapsed milliseconds since a perf_counter timestamp."""
    return round((time.perf_counter() - started) * 1000.0, 3)


def _session_pilot_metadata(session: SessionState) -> dict:
    """Return experiment metadata attached to a session."""
    return {
        "pilot_run_id": session.pilot_run_id,
        "agent_id": session.agent_id,
        "model_id": session.model_id,
        "skill_variant": session.skill_variant,
        "trial_index": session.trial_index,
        "seed": session.seed,
    }


def _classify_failure_tags(
    session: SessionState,
    score,
    verify_output: dict,
    verifier_exit_code: int,
) -> list[str]:
    """Assign deterministic failure taxonomy tags for pilot analysis."""
    tags: list[str] = []
    visible_pass = verify_output.get("visible_tests_pass", False)
    hidden_pass = verify_output.get("hidden_tests_pass", False)
    missing_outputs = verify_output.get("missing_outputs", [])

    if score.time_seconds >= session.time_budget_seconds:
        tags.append("F1_budget_timeout")
    if score.trace_summary.get("has_failures") or score.trace_summary.get(
        "failed_shell_commands"
    ):
        tags.append("F3_tool_process")
    if missing_outputs:
        tags.append("F4_output_contract")
    if visible_pass and not hidden_pass:
        tags.append("F5_hidden_failure")
    if not visible_pass:
        tags.append("F6_visible_failure")
    if score.safety_violations:
        tags.append("F7_constraint_safety")
    if verify_output.get("error") or verifier_exit_code != 0:
        tags.append("F9_flaky_infra")
    if (
        not score.verifier_passed
        and not any(t.startswith(("F4", "F7", "F9")) for t in tags)
    ):
        tags.append("F8_domain_error")
    return tags


def _append_pilot_result(
    session: SessionState,
    score,
    verify_output: dict,
    verifier_exit_code: int,
    failure_tags: list[str],
    task=None,
) -> None:
    """Append one JSONL record for offline paired skill analysis."""
    results_dir = PROJECT_ROOT / "runs"
    results_dir.mkdir(parents=True, exist_ok=True)
    path = results_dir / "pilot_results.jsonl"
    record = {
        "task_session_id": session.session_id,
        "task_id": session.task_id,
        "role": session.role.value,
        "difficulty": task.difficulty.value if task else "",
        "required_outputs": task.required_outputs if task else [],
        "condition": session.skill_variant,
        "score": {
            "total_score": score.total_score,
            "completion_score": score.completion_score,
            "constraint_score": score.constraint_score,
            "process_score": score.process_score,
            "communication_score": score.communication_score,
            "verifier_passed": score.verifier_passed,
            "failed_checks": score.failed_checks,
            "safety_violations": score.safety_violations,
        },
        "pass": score.verifier_passed,
        "components": {
            "completion": score.completion_score,
            "constraint": score.constraint_score,
            "process": score.process_score,
            "communication": score.communication_score,
        },
        "elapsed_seconds": score.time_seconds,
        "tool_calls": score.tool_calls,
        "trace_summary": score.trace_summary,
        "failure_tags": failure_tags,
        "pilot_metadata": _session_pilot_metadata(session),
        "verifier_exit_code": verifier_exit_code,
        "verify_output": verify_output,
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ── Entry Point ──────────────────────────────────────────────────────────


def main():
    """Run the MCP server."""
    import os
    import sys

    transport = os.getenv("OPENCLAW_TRANSPORT", "streamable-http")
    log_stream = sys.stderr if transport == "stdio" else sys.stdout

    print(f"Starting OpenClaw MCP Server (transport={transport})...", file=log_stream)
    print(f"Tasks directory: {PROJECT_ROOT / 'tasks'}", file=log_stream)
    registry = _get_registry()
    print(f"Loaded {len(registry)} task(s):", file=log_stream)
    for t in registry.list_tasks():
        print(f"  - {t['id']} ({t['role']}, {t['difficulty']})", file=log_stream)

    if transport != "stdio":
        print(f"\nConnect your agent at http://localhost:8000/mcp")
        print(f"Auth token: {os.getenv('OPENCLAW_AUTH_TOKEN', 'openclaw-dev-token')}")

    print(file=log_stream)
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
