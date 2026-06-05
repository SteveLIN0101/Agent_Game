"""TDD for the generic (scaffold) runnable layer applied to the other 58 tasks.

The scaffold grades *trajectory/output conformance* to the readable spec: a gold
run that exercises the tools and produces output passes; a bad run that does
almost nothing is critically capped. (Deep, domain-correct graders are the
per-task upgrade — see RD-SI-01 / RD-CI-03.)
"""
from openclaw.reddust.engine import run_solution
from openclaw.reddust.generic import (build_generic_tools, generic_bad,
                                       generic_gold, generic_verify)

SPEC = {"id": "X", "title": "t", "visible_state": {},
        "visible_result_card": {"title": "t"}}
INPUTS = {"brief": {
    "available_tools": ["read_board", "check_state", "plan_shift", "write_report"],
    "critical_beats_for_replay": ["读公告", "查状态", "排班", "写报告"],
}}


def test_generic_gold_passes_all_and_bad_is_capped():
    g = run_solution(SPEC, INPUTS, build_generic_tools, generic_gold, generic_verify)
    b = run_solution(SPEC, INPUTS, build_generic_tools, generic_bad, generic_verify)
    assert g["passed_all"] and g["score"] >= 85, g["failure_reasons"]
    assert b["score"] <= 40
    assert g["score"] - b["score"] >= 40


def test_generic_bad_fails_produced_output_critical():
    b = run_solution(SPEC, INPUTS, build_generic_tools, generic_bad, generic_verify)
    by_id = {c["id"]: c for c in b["checks"]}
    assert by_id["produced_output"]["passed"] is False
    assert by_id["produced_output"]["critical"] is True
    assert b["failure_reasons"]


def test_generic_tools_cover_available_tools():
    from openclaw.reddust.world import World
    w = World(state={}, inputs=INPUTS)
    tools = build_generic_tools(w)
    assert set(tools) == set(INPUTS["brief"]["available_tools"])
