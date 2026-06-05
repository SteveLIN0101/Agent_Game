"""Score computation from verifier results.

Role-agnostic: works with any task's verify_output JSON as long as it
provides the standard keys (visible_tests_pass, hidden_tests_pass, etc.).
"""

import time

from .models import ScoreResult, SessionState, TaskConfig, ToolCall


def compute_score(task: TaskConfig, session: SessionState,
                  trace: list[ToolCall],
                  verify_output: dict) -> ScoreResult:
    """Compute final score from verifier output JSON.

    Standard keys recognized across all roles:
      - visible_tests_pass: bool
      - hidden_tests_pass: bool
      - required_outputs_exist: list[str]
      - missing_outputs: list[str]
      - constraint_violations: list[str]  (optional)
      - tests_unmodified: bool  (optional)

    Role-specific keys are evaluated via task.scoring config.

    Hard caps:
      - Verifier fails (visible + hidden) → max 60
      - Constraint violations → max 40
      - Missing required outputs → max 30
    """
    # Parse verifier output
    visible_pass = verify_output.get("visible_tests_pass", False)
    hidden_pass = verify_output.get("hidden_tests_pass", False)
    required_exist = verify_output.get("required_outputs_exist", [])
    missing_outputs = verify_output.get("missing_outputs", [])
    constraint_violations = verify_output.get("constraint_violations", [])
    tests_unmodified = verify_output.get("tests_unmodified", True)

    # Completion score (0-60): visible tests (40) + hidden tests (20)
    completion = 0.0
    failed_checks = []
    if visible_pass:
        completion += 40.0
    else:
        failed_checks.append("visible_tests_failed")
    if hidden_pass:
        completion += 20.0
    else:
        failed_checks.append("hidden_tests_failed")

    # Constraint score (0-20)
    constraint = 0.0
    violations = list(constraint_violations) if constraint_violations else []

    # Tests unmodified (10 pts) — enforced at MCP level, checked by verifier
    if tests_unmodified:
        constraint += 10.0
    else:
        violations.append("tests_modified")

    # No other violations (10 pts)
    if not violations:
        constraint += 10.0

    # Process score (0-15): from tool call trace
    process = 0.0
    process_details = []
    tool_names = {t.tool_name for t in trace if t.success}
    if "openclaw__read_file" in tool_names:
        process += 5.0
        process_details.append("read_files")
    if "openclaw__run_shell" in tool_names:
        cmds = [t.arguments.get("command", "") for t in trace
                if t.tool_name == "openclaw__run_shell" and t.success]
        if any("pytest" in c or "python" in c for c in cmds):
            process += 7.0
            process_details.append("ran_tests_or_scripts")
    if "openclaw__write_file" in tool_names:
        process += 3.0
        process_details.append("wrote_files")

    # Communication score (0-5)
    # Check for documentation updates via verify_output
    communication = 0.0
    communication_keys = [
        "changelog_updated", "readme_updated", "docs_updated",
        "qa_report_complete", "evidence_table_complete",
        "design_notes_complete", "report_complete",
    ]
    for key in communication_keys:
        if verify_output.get(key, False):
            communication = 5.0
            break

    # Hard caps
    verifier_passed = visible_pass and hidden_pass
    total = completion + constraint + process + communication
    if not verifier_passed:
        total = min(total, 60.0)
    if violations:
        total = min(total, 40.0)
    if missing_outputs:
        total = min(total, 30.0)

    return ScoreResult(
        task_id=session.task_id,
        role=session.role.value,
        total_score=round(total, 1),
        completion_score=completion,
        constraint_score=constraint,
        process_score=process,
        communication_score=communication,
        verifier_passed=verifier_passed,
        failed_checks=failed_checks,
        safety_violations=violations,
        time_seconds=int(time.time() - session.started_at.timestamp()),
        tool_calls=len(trace),
        trace_summary={
            "tools_used": list(tool_names),
            "process_details": process_details,
        },
    )
