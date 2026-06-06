import http.client
import json
import threading
from pathlib import Path

from openclaw.reddust.campaign import CampaignService, CampaignSlot, DEFAULT_CAMPAIGN_SLOTS
from openclaw.reddust.lan_server import RedDustLanService, make_http_server
from openclaw.reddust.story_manifest import (
    BRANCH_SCENES,
    ENDINGS,
    PROLOGUE_EVENT,
    READABLE_TASK_SLOTS,
    STORY_VERSION,
    story_manifest_public,
)


ROOT = Path(__file__).resolve().parents[1]


def post_json(port: int, path: str, payload: dict) -> tuple[int, dict]:
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    conn.request(
        "POST",
        path,
        body=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    resp = conn.getresponse()
    body = resp.read().decode("utf-8")
    conn.close()
    return resp.status, json.loads(body)


def get_json(port: int, path: str) -> tuple[int, dict]:
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    conn.request("GET", path)
    resp = conn.getresponse()
    body = resp.read().decode("utf-8")
    conn.close()
    return resp.status, json.loads(body)


def test_campaign_map_references_and_covers_all_red_dust_tasks(tmp_path):
    lan = RedDustLanService(tasks_dir=ROOT / "tasks", run_dir=tmp_path / "lan")
    CampaignService(lan, run_dir=tmp_path / "campaigns")

    real_task_ids = {meta["task_id"] for meta in lan.list_tasks()["tasks"]}
    pooled_task_ids = {task_id for slot in DEFAULT_CAMPAIGN_SLOTS for task_id in slot.task_pool}
    slot_ids = {slot.slot_id for slot in READABLE_TASK_SLOTS}
    expected_slot_ids = {f"D{day:02d}-T{idx:02d}" for day in range(1, 12) for idx in range(1, 5)}

    assert len(DEFAULT_CAMPAIGN_SLOTS) == 44
    assert slot_ids == expected_slot_ids
    assert pooled_task_ids == real_task_ids
    assert {scene["id"] for scene in BRANCH_SCENES} == {"D08A", "D09A", "D10A", "D08B", "D09B", "D10B"}
    assert {ending["title"] for ending in ENDINGS.values()} == {"楼内灯塔", "蓝区归航", "AURA 被摧毁", "AURA 被撤权", "沉沦"}
    manifest = story_manifest_public()
    assert manifest["story_version"] == STORY_VERSION
    assert manifest["prologue"]["id"] == "D00"
    assert manifest["prologue"]["beats"]
    assert "aura_authority_limited" in manifest["prologue"]["flags"]
    assert "manual_review_rules" not in manifest["prologue"]["flags"]
    assert "manual_review_rules" not in manifest["prologue"].get("unlocks", [])
    assert manifest["final_audit"]["id"] == "D12"


def test_story_manifest_public_day1_day6_risk_delta_overrides():
    manifest = story_manifest_public()
    slots = {slot["slot_id"]: slot for slot in manifest["task_slots"]}

    assert slots["D04-T02"]["task_pool"] == ["RD-PF-04"]
    assert "RD-CS-10" not in slots["D04-T02"]["task_pool"]
    assert slots["D04-T04"]["location"] == "communication"
    assert slots["D05-T01"]["event_options"] == ["conditional"]
    assert slots["D06-T01"]["task_pool"] == ["RD-SA-01", "RD-CS-08", "RD-SR-10"]
    assert slots["D06-T04"]["task_pool"] == ["RD-CI-09"]
    assert slots["D06-T04"]["location"] == "communication"
    assert slots["D06-T03"]["event_options"] == ["optional"]

    expectations = [
        ("D01-T01", "failure", "outside_risk", 1, ">="),
        ("D01-T03", "failure", "outside_risk", 1, ">="),
        ("D02-T04", "failure", "outside_risk", 1, ">="),
        ("D02-T04", "missing", "outside_risk", 1, ">="),
        ("D03-T01", "failure", "medical_pressure", 1, ">="),
        ("D03-T01", "missing", "medical_pressure", 1, ">="),
        ("D03-T01", "failure", "xiao_tie_health", -1, "<="),
        ("D03-T02", "failure", "outside_risk", 1, ">="),
        ("D03-T02", "failure", "ventilation_stability", -1, "<="),
        ("D03-T03", "failure", "medical_pressure", 1, ">="),
        ("D04-T03", "failure", "false_signal_risk", 1, ">="),
        ("D04-T01", "failure", "outside_risk", 1, ">="),
        ("D04-T01", "failure", "false_signal_risk", 1, ">="),
        ("D04-T02", "failure", "outside_risk", 1, ">="),
        ("D04-T02", "failure", "false_signal_risk", 1, ">="),
        ("D04-T04", "failure", "maintenance_debt", 1, ">="),
        ("D04-T04", "failure", "battery", -1, "<="),
        ("D05-T01", "failure", "outside_risk", 1, ">="),
        ("D05-T01", "missing", "outside_risk", 1, ">="),
        ("D05-T02", "failure", "route_confidence", -1, "<="),
        ("D05-T03", "failure", "emergency_pack_readiness", -1, "<="),
        ("D05-T04", "failure", "water_storage_readiness", -1, "<="),
        ("D06-T01", "failure", "dissatisfaction", 1, ">="),
        ("D06-T01", "failure", "aura_authority_risk", 1, ">="),
        ("D06-T02", "failure", "dissatisfaction", 1, ">="),
        ("D06-T02", "failure", "sacrifice_list_risk", 1, ">="),
        ("D06-T03", "failure", "outside_risk", 1, ">="),
        ("D06-T03", "failure", "dissatisfaction", 1, ">="),
        ("D06-T04", "success", "battery", -1, "<="),
        ("D06-T04", "success", "power_stability", 1, ">="),
        ("D06-T04", "failure", "battery", -1, "<="),
        ("D06-T04", "failure", "maintenance_debt", 1, ">="),
    ]
    for slot_id, outcome, key, threshold, op in expectations:
        value = slots[slot_id]["outcome_deltas"][outcome][key]
        if op == ">=":
            assert value >= threshold, (slot_id, outcome, key, value)
        else:
            assert value <= threshold, (slot_id, outcome, key, value)


def test_day0_prologue_trace_is_structured_without_task_session(tmp_path):
    lan = RedDustLanService(tasks_dir=ROOT / "tasks", run_dir=tmp_path / "lan")
    campaign = CampaignService(lan, run_dir=tmp_path / "campaigns")

    state = campaign.create_campaign({
        "seed": "day0-structured",
        "branch_policy": "rescue",
        "task_selection": "first",
    })
    cid = state["campaign_id"]

    assert state["current_slot_id"] == "D01-T02"
    assert state["current_run"]["slot_id"] == "D01-T02"
    assert len(campaign.sessions[cid].task_runs) == 1
    assert "aura_authority_limited" in state["story_flags"]
    assert "manual_review_rules" not in state["story_flags"]

    day0_replay = state["replay_log"][0]
    assert day0_replay["slot_id"] == "D00"
    assert day0_replay["task_id"] == ""
    assert day0_replay["story_event"]["beats"][0]["id"] == "D00-B01"
    assert "replay_started" in day0_replay["story_flags"]
    assert day0_replay["replay_text"]

    story_events = [event for event in state["events"] if event["type"] == "story_event"]
    assert len(story_events) == 1
    story_event = story_events[0]["payload"]["story_event"]
    assert story_event["id"] == "D00"
    assert story_event["beats"] == PROLOGUE_EVENT["beats"]
    assert "aura_authority_limited" in story_event["flags"]
    assert story_event["replay_text"]

    trace = campaign.trace_campaign(cid)
    first_frontend_event = trace["frontend_trace"][0]
    assert first_frontend_event["phase_hint"] == "story_event"
    assert first_frontend_event["frontend_task"]["id"] == "D00"
    assert first_frontend_event["frontend_task"]["beats"]
    assert first_frontend_event["replay_event"]["story_event"]["flags"] == PROLOGUE_EVENT["flags"]


def test_campaign_seeded_task_selection_is_reproducible(tmp_path):
    lan_a = RedDustLanService(tasks_dir=ROOT / "tasks", run_dir=tmp_path / "lan_a")
    lan_b = RedDustLanService(tasks_dir=ROOT / "tasks", run_dir=tmp_path / "lan_b")
    campaign_a = CampaignService(lan_a, run_dir=tmp_path / "campaigns_a")
    campaign_b = CampaignService(lan_b, run_dir=tmp_path / "campaigns_b")

    state_a = campaign_a.create_campaign({"seed": "20260603", "branch_policy": "rescue"})
    state_b = campaign_b.create_campaign({"seed": "20260603", "branch_policy": "rescue"})

    assert state_a["current_slot_id"] == "D01-T02"
    assert state_a["current_task_id"] == state_b["current_task_id"]


def test_campaign_state_machine_can_complete_single_branch_with_submits(tmp_path):
    lan = RedDustLanService(tasks_dir=ROOT / "tasks", run_dir=tmp_path / "lan")
    campaign = CampaignService(lan, run_dir=tmp_path / "campaigns")
    state = campaign.create_campaign({
        "seed": "state-machine",
        "branch_policy": "rescue",
        "task_selection": "first",
        "max_steps_per_task": 1,
    })
    cid = state["campaign_id"]

    guard = 0
    while campaign.get_state(cid)["status"] != "complete":
        campaign.submit_current(cid)
        guard += 1
        assert guard <= 50

    done = campaign.get_state(cid)
    assert done["status"] == "complete"
    assert done["story_version"] == STORY_VERSION
    assert len(done["completed_slots_list"]) == 44
    assert done["replay_log"][0]["slot_id"] == "D00"
    assert done["replay_log"][-1]["slot_id"] == "D12"
    trace = campaign.trace_campaign(cid)
    phase_hints = {item["phase_hint"] for item in trace["frontend_trace"]}
    assert {"story_event", "branch_scene", "final_audit", "replay_logged"}.issubset(phase_hints)
    assert trace["frontend_trace"][0]["frontend_task"]["id"] == "D00"
    assert trace["frontend_trace"][-1]["frontend_task"]["id"] == "D12"
    assert (tmp_path / "campaigns" / cid / "campaign.json").exists()
    assert (tmp_path / "campaigns" / cid / "report.html").exists()


def test_campaign_gold_helper_runs_current_real_task(tmp_path):
    slot = CampaignSlot(
        slot_id="SMOKE-SI-01",
        day=1,
        branch="common",
        story_title="三轮取水行动协商",
        location="residents",
        task_pool=("RD-SI-01",),
        state_delta={"trust": 5, "water": 3},
    )
    lan = RedDustLanService(tasks_dir=ROOT / "tasks", run_dir=tmp_path / "lan")
    campaign = CampaignService(lan, run_dir=tmp_path / "campaigns", slots=(slot,))
    state = campaign.create_campaign({"seed": "gold", "branch_policy": "rescue"})
    cid = state["campaign_id"]

    result = campaign.run_solution_current(cid, "gold")

    submitted = result["submitted_result"]
    assert submitted["score"] >= 85
    assert result["state"]["status"] == "complete"
    task_events = [event for event in result["state"]["replay_log"] if event.get("task_id") == "RD-SI-01"]
    assert task_events[0]["outcome"] == "success"


def test_campaign_http_endpoints_expose_brief_and_submit(tmp_path):
    lan = RedDustLanService(tasks_dir=ROOT / "tasks", run_dir=tmp_path / "lan")
    campaign = CampaignService(lan, run_dir=tmp_path / "campaigns")
    server = make_http_server(lan, host="127.0.0.1", port=0, campaign_service=campaign)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, health = get_json(port, "/health")
        assert status == 200
        assert health["campaigns"] == 0

        status, created = post_json(port, "/campaigns", {
            "seed": "http",
            "branch_policy": "rescue",
            "task_selection": "first",
            "max_steps_per_task": 1,
        })
        assert status == 201
        cid = created["campaign_id"]

        status, brief = get_json(port, f"/campaigns/{cid}/brief")
        assert status == 200
        assert "Red Dust Day0-12" in brief["brief"]
        assert brief["current_task_id"] == "RD-PF-03"

        status, submitted = post_json(port, f"/campaigns/{cid}/submit", {})
        assert status == 200
        assert submitted["ok"] is True
        assert submitted["state"]["current_slot_id"] == "D01-T01"

        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
        conn.request("GET", f"/campaigns/{cid}/report.html")
        resp = conn.getresponse()
        body = resp.read().decode("utf-8")
        conn.close()
        assert resp.status == 200
        assert "Red Dust Campaign" in body
    finally:
        server.shutdown()
        server.server_close()


def test_campaign_connect_start_gate_and_event_polling(tmp_path):
    slot = CampaignSlot(
        slot_id="SMOKE-SI-01",
        day=1,
        branch="common",
        story_title="三轮取水行动协商",
        location="residents",
        task_pool=("RD-SI-01",),
        state_delta={"trust": 5, "water": 3},
    )
    lan = RedDustLanService(tasks_dir=ROOT / "tasks", run_dir=tmp_path / "lan")
    campaign = CampaignService(lan, run_dir=tmp_path / "campaigns", slots=(slot,))
    state = campaign.create_campaign({
        "seed": "gate",
        "wait_for_start": True,
        "branch_policy": "rescue",
    })
    cid = state["campaign_id"]

    blocked = campaign.take_action(cid, {"tool": "read_note_board", "args": {}})
    assert blocked["ok"] is False
    assert blocked["error"] == "waiting_for_start"

    connected = campaign.connect_agent(cid, {
        "agent_id": "pytest-agent",
        "model_id": "fake",
        "client": "pytest",
    })
    assert connected["ok"] is True
    events = campaign.get_events(cid, after=0)["events"]
    assert any(event["type"] == "agent_connected" for event in events)

    latest_before = campaign.get_events(cid, after=0)["latest_seq"]
    assert campaign.get_events(cid, after=latest_before)["events"] == []

    started = campaign.start_campaign(cid)
    assert started["state"]["status"] == "running"
    allowed = campaign.take_action(cid, {"tool": "read_note_board", "args": {}})
    assert allowed["ok"] is True
    new_events = campaign.get_events(cid, after=latest_before)["events"]
    assert [event["type"] for event in new_events] == ["campaign_started", "action_executed"]


def test_campaign_archive_trace_is_readable_after_service_restart(tmp_path):
    slot = CampaignSlot(
        slot_id="SMOKE-SI-01",
        day=1,
        branch="common",
        story_title="三轮取水行动协商",
        location="residents",
        task_pool=("RD-SI-01",),
        state_delta={"trust": 5, "water": 3},
    )
    lan = RedDustLanService(tasks_dir=ROOT / "tasks", run_dir=tmp_path / "lan")
    campaign = CampaignService(lan, run_dir=tmp_path / "campaigns", slots=(slot,))
    state = campaign.create_campaign({"seed": "archive", "branch_policy": "rescue"})
    cid = state["campaign_id"]
    campaign.run_solution_current(cid, "gold")

    restarted_lan = RedDustLanService(tasks_dir=ROOT / "tasks", run_dir=tmp_path / "lan_restart")
    restarted = CampaignService(restarted_lan, run_dir=tmp_path / "campaigns", slots=(slot,))
    trace = restarted.trace_campaign(cid)

    assert trace["read_only"] is True
    assert trace["status"] == "complete"
    assert len(trace["frontend_trace"]) >= 3
    assert trace["frontend_trace"][0]["state_before"]
    assert trace["frontend_trace"][0]["state_after"]
    assert restarted.get_events(cid, after=0)["events"]
    assert "Red Dust Campaign" in restarted.render_report(cid)
