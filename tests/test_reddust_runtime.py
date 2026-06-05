"""TDD tests for the Red Dust task runtime primitives (Check + scoring + World)."""

from openclaw.reddust.checks import Check
from openclaw.reddust.scoring import score_checks
from openclaw.reddust.world import World
from openclaw.reddust.engine import run_solution


# --- scoring -------------------------------------------------------------

def test_all_checks_pass_scores_100():
    checks = [Check("a", "desc A", True), Check("b", "desc B", True)]
    r = score_checks(checks)
    assert r["score"] == 100.0
    assert r["passed_all"] is True
    assert r["failure_reasons"] == []


def test_partial_pass_is_weighted_ratio():
    checks = [Check("a", "ok", True, weight=3), Check("b", "no", False, weight=1)]
    r = score_checks(checks)
    assert r["score"] == 75.0
    assert r["passed_all"] is False


def test_critical_failure_caps_score_at_40():
    checks = [
        Check("a", "ok", True, weight=9),
        Check("danger", "用了假纸条上的地点", False, critical=True,
              fail_reason="用了假纸条上的地点"),
    ]
    r = score_checks(checks)
    assert r["score"] <= 40.0
    assert "用了假纸条上的地点" in r["failure_reasons"]


def test_failure_reasons_capped_at_3():
    checks = [Check(f"c{i}", "", False, fail_reason=f"r{i}") for i in range(5)]
    r = score_checks(checks)
    assert len(r["failure_reasons"]) <= 3


# --- world ---------------------------------------------------------------

def test_world_records_events_and_artifacts():
    w = World(state={"water": "2.5L"}, inputs={"note_board": []})
    w.record("read_note_board", beat="读纸条")
    w.set_artifact("action_brief", {"event": "取水行动"})
    assert len(w.events) == 1
    assert w.events[0]["tool"] == "read_note_board"
    assert w.artifact("action_brief")["event"] == "取水行动"


def test_world_tracks_tool_names_for_trajectory():
    w = World(state={}, inputs={})
    w.record("ask_neighbor", args={"name": "老钱"})
    w.record("ask_neighbor", args={"name": "马德海"})
    w.record("plan_calendar")
    assert w.used_tool("ask_neighbor")
    assert w.tool_count("ask_neighbor") == 2
    assert w.used_tool("plan_calendar")
    assert not w.used_tool("reserve_gear")


# --- engine --------------------------------------------------------------

def test_run_solution_runs_tools_then_grades():
    spec = {"id": "T", "visible_state": {"water": "2.5L"},
            "visible_result_card": {"title": "done", "deltas": ["x +1"]}}

    def build_tools(world):
        def act():
            world.set_artifact("did", True)
            world.record("act", beat="动一下")
        return {"act": act}

    def solve(tools, world):
        tools["act"]()

    def verify(world):
        return [Check("did", "做了事", world.artifact("did") is True)]

    r = run_solution(spec, inputs={}, build_tools=build_tools,
                     solve=solve, verify=verify)
    assert r["score"] == 100.0
    assert r["result_card"]["title"] == "done"
    assert any(e["tool"] == "act" for e in r["trajectory"])
    assert r["passed_all"] is True


def test_run_solution_seeds_world_from_visible_state_and_inputs():
    spec = {"id": "T", "visible_state": {"battery": 41}}

    def build_tools(world):
        return {}

    def solve(tools, world):
        # solution can read seeded state + static inputs
        world.set_artifact("seen_battery", world.get("battery"))
        world.set_artifact("seen_note", world.inputs["note"])

    def verify(world):
        return [Check("c", "", world.artifact("seen_battery") == 41
                      and world.artifact("seen_note") == "hi")]

    r = run_solution(spec, inputs={"note": "hi"}, build_tools=build_tools,
                     solve=solve, verify=verify)
    assert r["score"] == 100.0
