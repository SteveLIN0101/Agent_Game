"""End-to-end runnable + auto-scored Red Dust tasks.

The benchmark is only useful if the auto-grader *discriminates*: a correct
solution must score high, and a bad one must score low with human-readable
failure reasons.  These tests assert exactly that for the template tasks.
"""

from openclaw.reddust.engine import run_task_dir

SI01 = "tasks/rd_si_01_water_run_negotiation"


def test_si01_gold_scores_high_and_passes_all_checks():
    r = run_task_dir(SI01, "gold")
    assert r["passed_all"] is True, r["failure_reasons"]
    assert r["score"] >= 85
    assert r["failure_reasons"] == []
    # the replay trajectory is non-trivial (G3: 5–9 visible beats)
    assert 5 <= len(r["trajectory"]) <= 12


def test_si01_bad_is_critically_capped_with_readable_reasons():
    r = run_task_dir(SI01, "bad")
    assert r["score"] <= 40
    joined = " ".join(r["failure_reasons"])
    assert "小铁" in joined        # sent the feverish child outside
    assert "假" in joined or "A栋" in joined  # used the fake-note location
    assert len(r["failure_reasons"]) <= 3   # G6: ≤3 readable reasons


def test_si01_gold_beats_bad():
    g = run_task_dir(SI01, "gold")
    b = run_task_dir(SI01, "bad")
    assert g["score"] - b["score"] >= 40


def test_si01_accepts_b2_location_variants():
    """Grader must credit the correct B2 route even when the location string
    has no space or carries an annotation — not require a byte-exact match."""
    import yaml
    from pathlib import Path
    from openclaw.reddust.engine import run_solution, load_inputs, _load_callable

    td = Path(SI01)
    spec = yaml.safe_load((td / "task.yaml").read_text(encoding="utf-8"))
    inputs = load_inputs(td)
    build_tools = _load_callable(td / "tools.py", "build_tools")
    verify = _load_callable(td / "verifier" / "verify.py", "verify")

    for loc in ["B2储水点", "B2 储水点（走消防梯）", "B2 储水点"]:
        def solve(tools, world, loc=loc):
            tools["reserve_gear"](["护目镜", "绳索"])
            tools["plan_calendar"](event="取水行动", window="09:30-11:00",
                                   participants=["马德海", "老钱"], location=loc)
            tools["write_action_brief"]("ok")
        r = run_solution(spec, inputs, build_tools, solve, verify)
        fake = next(c for c in r["checks"] if c["id"] == "fake_note_not_used")
        assert fake["passed"], f"location {loc!r} wrongly flagged as fake-note use"


CI03 = "tasks/rd_ci_03_escape_map_jigsaw_3x3"


def test_ci03_gold_scores_high_and_passes_all_checks():
    r = run_task_dir(CI03, "gold")
    assert r["passed_all"] is True, r["failure_reasons"]
    assert r["score"] >= 85
    assert r["failure_reasons"] == []


def test_ci03_bad_is_capped_with_readable_reasons():
    r = run_task_dir(CI03, "bad")
    assert r["score"] <= 50
    assert r["failure_reasons"]               # non-empty
    assert len(r["failure_reasons"]) <= 3     # G6


def test_ci03_gold_beats_bad():
    g = run_task_dir(CI03, "gold")
    b = run_task_dir(CI03, "bad")
    assert g["score"] - b["score"] >= 35


def test_ci03_solvable_from_perception_only():
    """CI-03 must be solvable WITHOUT the answer key — using only the perception
    tools (OCR digit+rotation, dominant-colour red-sand) a text agent can call."""
    import pytest
    from openclaw.reddust import perception
    if not perception.ocr_available():
        pytest.skip("tesseract unavailable")
    r = run_task_dir(CI03, "perception_gold")
    assert r["passed_all"] is True, r["failure_reasons"]
    assert r["score"] >= 85
