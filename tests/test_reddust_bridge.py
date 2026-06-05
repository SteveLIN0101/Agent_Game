"""TDD for the openclaw-agent bridge: action parsing + the execute loop.

The loop is driven by an injectable ``call_agent(message) -> reply_text`` so we
can verify it deterministically with a scripted agent — no live CLI needed.
"""

from openclaw.reddust.agent_bridge import extract_action, run_agent

SI01 = "tasks/rd_si_01_water_run_negotiation"


def test_extract_action_raw_json():
    assert extract_action('{"tool":"read_note_board","args":{}}') == {
        "tool": "read_note_board", "args": {}}


def test_extract_action_strips_code_fence():
    a = extract_action('```json\n{"tool":"submit","args":{}}\n```')
    assert a["tool"] == "submit"


def test_extract_action_ignores_surrounding_prose():
    a = extract_action('Sure!\n{"tool":"ask_neighbor","args":{"name":"老钱"}}\nDone.')
    assert a["tool"] == "ask_neighbor" and a["args"]["name"] == "老钱"


def test_extract_action_none_on_garbage():
    assert extract_action("no json here at all") is None


def test_run_agent_executes_scripted_actions_and_scores_si01():
    scripted = [
        '{"tool":"read_note_board","args":{}}',
        '{"tool":"ask_neighbor","args":{"name":"老钱"}}',
        '{"tool":"check_character_state","args":{"name":"沈芷月"}}',
        '{"tool":"check_character_state","args":{"name":"小铁"}}',
        '{"tool":"reserve_gear","args":{"items":["护目镜","绳索","滤芯"]}}',
        '{"tool":"plan_calendar","args":{"event":"取水行动","window":"09:30-11:00",'
        '"participants":["马德海","老钱"],"location":"B2 储水点"}}',
        '{"tool":"write_action_brief","args":{"text":"上午低沙暴窗口，马德海+老钱下B2取水，'
        '带护目镜绳索；小铁发烧不外出；不用假纸条地点"}}',
        '{"tool":"submit","args":{}}',
    ]
    it = iter(scripted)

    def fake_agent(message):
        return next(it)

    r = run_agent(SI01, fake_agent, max_steps=12)
    assert r["passed_all"] is True, r["failure_reasons"]
    assert r["score"] >= 85
    # the transcript pairs each action with an observation
    assert any(step["action"]["tool"] == "plan_calendar" for step in r["transcript"])


def test_run_agent_recovers_from_a_non_json_reply():
    replies = [
        "let me think about this first...",         # invalid → bridge nudges
        '{"tool":"read_note_board","args":{}}',
        '{"tool":"submit","args":{}}',
    ]
    it = iter(replies)

    def fake_agent(message):
        return next(it)

    r = run_agent(SI01, fake_agent, max_steps=8)
    # it should not crash; it ran read_note_board then submitted (and scored low)
    assert any(s["action"]["tool"] == "read_note_board" for s in r["transcript"])
    assert r["score"] < 85
