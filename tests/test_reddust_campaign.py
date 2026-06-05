import http.client
import json
import threading
from pathlib import Path

from openclaw.reddust.campaign import CampaignService, CampaignSlot, DEFAULT_CAMPAIGN_SLOTS
from openclaw.reddust.lan_server import RedDustLanService, make_http_server


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

    assert len(DEFAULT_CAMPAIGN_SLOTS) == 33
    assert pooled_task_ids == real_task_ids
    assert any(slot.event_kind == "random_event" for slot in DEFAULT_CAMPAIGN_SLOTS)


def test_campaign_seeded_task_selection_is_reproducible(tmp_path):
    lan_a = RedDustLanService(tasks_dir=ROOT / "tasks", run_dir=tmp_path / "lan_a")
    lan_b = RedDustLanService(tasks_dir=ROOT / "tasks", run_dir=tmp_path / "lan_b")
    campaign_a = CampaignService(lan_a, run_dir=tmp_path / "campaigns_a")
    campaign_b = CampaignService(lan_b, run_dir=tmp_path / "campaigns_b")

    state_a = campaign_a.create_campaign({"seed": "20260603", "branch_policy": "rescue"})
    state_b = campaign_b.create_campaign({"seed": "20260603", "branch_policy": "rescue"})

    assert state_a["current_slot_id"] == "RD-WATER-01"
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
        assert guard <= 40

    done = campaign.get_state(cid)
    assert done["status"] == "complete"
    assert done["ending"]["branch"] == "rescue"
    assert len(done["completed_slots_list"]) == 27
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
    assert result["state"]["replay_log"][0]["outcome"] == "success"


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
        assert "Red Dust 10 天 campaign" in brief["brief"]
        assert brief["current_task_id"] == "RD-PF-02"

        status, submitted = post_json(port, f"/campaigns/{cid}/submit", {})
        assert status == 200
        assert submitted["ok"] is True
        assert submitted["state"]["current_slot_id"] == "RD-MED-01"

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
    assert len(trace["frontend_trace"]) == 1
    assert trace["frontend_trace"][0]["state_before"]
    assert trace["frontend_trace"][0]["state_after"]
    assert restarted.get_events(cid, after=0)["events"]
    assert "Red Dust Campaign" in restarted.render_report(cid)
