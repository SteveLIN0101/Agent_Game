import http.client
import json
import threading
from pathlib import Path

from openclaw.reddust.lan_server import RedDustLanService, make_http_server


ROOT = Path(__file__).resolve().parents[1]


SI01_ACTIONS = [
    {"tool": "read_note_board", "args": {}},
    {"tool": "ask_neighbor", "args": {"name": "老钱"}},
    {"tool": "check_character_state", "args": {"name": "沈芷月"}},
    {"tool": "check_character_state", "args": {"name": "小铁"}},
    {"tool": "reserve_gear", "args": {"items": ["护目镜", "绳索", "滤芯"]}},
    {
        "tool": "plan_calendar",
        "args": {
            "event": "取水行动",
            "window": "09:30-11:00",
            "participants": ["马德海", "老钱"],
            "location": "B2 储水点",
        },
    },
    {
        "tool": "write_action_brief",
        "args": {
            "text": "上午低沙暴窗口，马德海+老钱下B2取水，带护目镜绳索；小铁发烧不外出；不用假纸条地点"
        },
    },
]


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


def test_lan_service_runs_scripted_session_and_persists_report(tmp_path):
    service = RedDustLanService(tasks_dir=ROOT / "tasks", run_dir=tmp_path)

    created = service.create_session({
        "task_id": "RD-SI-01",
        "agent_id": "pytest",
        "max_steps": 12,
    })
    sid = created["session_id"]
    brief = service.get_brief(sid)
    assert "RD-SI-01" in brief["brief"]
    assert any(t["name"] == "read_note_board" for t in brief["tools"])

    for action in SI01_ACTIONS:
        result = service.take_action(sid, action)
        assert result["ok"] is True, result

    submitted = service.submit_session(sid)
    score = submitted["result"]["score"]
    assert score >= 85, submitted["result"]["failure_reasons"]
    assert submitted["result"]["passed_all"] is True

    trace = service.trace_session(sid)
    assert trace["submitted"] is True
    assert len(trace["transcript"]) >= len(SI01_ACTIONS)
    assert (tmp_path / sid / "session.json").exists()
    assert (tmp_path / sid / "report.html").exists()


def test_lan_http_server_minimal_remote_loop(tmp_path):
    service = RedDustLanService(tasks_dir=ROOT / "tasks", run_dir=tmp_path)
    server = make_http_server(service, host="127.0.0.1", port=0)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, health = get_json(port, "/health")
        assert status == 200
        assert health["tasks"] == 60

        status, created = post_json(port, "/sessions", {
            "task_id": "RD-SR-11",
            "agent_id": "pytest-http",
            "max_steps": 6,
        })
        assert status == 201
        sid = created["session_id"]

        status, action_result = post_json(port, f"/sessions/{sid}/actions", {
            "tool": "search_sources",
            "args": {"query": "offline LLM animal C++ gguf"},
        })
        assert status == 200
        assert action_result["ok"] is True

        status, submitted = post_json(port, f"/sessions/{sid}/submit", {})
        assert status == 200
        assert submitted["done"] is True
        assert "score" in submitted["result"]

        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
        conn.request("GET", f"/sessions/{sid}/report.html")
        resp = conn.getresponse()
        body = resp.read().decode("utf-8")
        conn.close()
        assert resp.status == 200
        assert "Red Dust LAN Report" in body
    finally:
        server.shutdown()
        server.server_close()
