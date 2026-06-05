"""LAN HTTP server for remote agents to play Red Dust tasks.

This module exposes the existing Red Dust runtime through a small REST surface:
remote agents create sessions, send JSON actions, receive observations, submit,
and inspect score/trace/report artifacts.  It intentionally reuses the same
``{"tool": ..., "args": ...}`` protocol as :mod:`openclaw.reddust.agent_bridge`.
"""

from __future__ import annotations

import argparse
import html
import inspect
import json
import os
import socket
import time
import traceback
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import yaml

from .agent_bridge import _signature_hint, _tool_catalog, build_brief
from .campaign import CampaignService
from .engine import _load_callable, load_inputs
from .scoring import score_checks
from .world import World


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TASKS_DIR = ROOT / "tasks"
DEFAULT_RUN_DIR = ROOT / "runs" / "reddust_lan_sessions"


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def jsonable(value: Any) -> Any:
    """Return a JSON-safe representation without losing useful structure."""
    try:
        json.dumps(value, ensure_ascii=False)
        return value
    except TypeError:
        if isinstance(value, dict):
            return {str(k): jsonable(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [jsonable(v) for v in value]
        return str(value)


def read_json_body(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length") or 0)
    if length <= 0:
        return {}
    raw = handler.rfile.read(length)
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


def task_meta(task_dir: Path) -> dict[str, Any]:
    spec = yaml.safe_load((task_dir / "task.yaml").read_text(encoding="utf-8"))
    return {
        "task_id": spec.get("id"),
        "slug": task_dir.name,
        "title": spec.get("title", ""),
        "category": spec.get("category", ""),
        "modality": spec.get("modality", ""),
        "user_visible_goal": spec.get("user_visible_goal", ""),
        "visible_state": spec.get("visible_state", {}),
        "available_tools": spec.get("available_tools", []),
        "success_checks": spec.get("success_checks", []),
        "critical_beats_for_replay": spec.get("critical_beats_for_replay", []),
        "story_metadata": spec.get("story_metadata", {}),
    }


@dataclass
class RedDustSession:
    session_id: str
    task_dir: Path
    spec: dict[str, Any]
    world: World
    tools: dict[str, Any]
    verify: Any
    max_steps: int
    agent_id: str = ""
    model_id: str = ""
    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)
    used_steps: int = 0
    submitted: bool = False
    result: dict[str, Any] | None = None
    transcript: list[dict[str, Any]] = field(default_factory=list)

    @property
    def task_id(self) -> str:
        return self.spec.get("id") or self.task_dir.name

    @property
    def title(self) -> str:
        return self.spec.get("title", "")

    def tool_schema(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for name, fn in self.tools.items():
            doc = (inspect.getdoc(fn) or "").strip().splitlines()
            out.append({
                "name": name,
                "args_hint": _signature_hint(name, fn),
                "description": doc[0] if doc else "",
            })
        out.append({
            "name": "submit",
            "args_hint": "{}",
            "description": "Submit the current run for scoring.",
        })
        return out


class RedDustLanService:
    """In-memory session service with optional JSON/report persistence."""

    def __init__(
        self,
        *,
        tasks_dir: str | Path = DEFAULT_TASKS_DIR,
        run_dir: str | Path = DEFAULT_RUN_DIR,
        public_base_url: str = "",
    ) -> None:
        self.tasks_dir = Path(tasks_dir)
        self.run_dir = Path(run_dir)
        self.public_base_url = public_base_url.rstrip("/")
        self.sessions: dict[str, RedDustSession] = {}
        self._task_index: dict[str, Path] = {}
        self._task_metas: list[dict[str, Any]] = []
        self._discover_tasks()

    def _discover_tasks(self) -> None:
        self._task_index.clear()
        self._task_metas.clear()
        for task_dir in sorted(self.tasks_dir.glob("rd_*")):
            if not (task_dir / "task.yaml").exists():
                continue
            meta = task_meta(task_dir)
            if not meta.get("task_id"):
                continue
            self._task_index[meta["task_id"]] = task_dir
            self._task_index[task_dir.name] = task_dir
            self._task_metas.append(meta)

    def health(self) -> dict[str, Any]:
        return {
            "ok": True,
            "service": "red-dust-lan-server",
            "time": now_iso(),
            "tasks": len(self._task_metas),
            "sessions": len(self.sessions),
        }

    def list_tasks(self) -> dict[str, Any]:
        return {"tasks": self._task_metas, "count": len(self._task_metas)}

    def get_task(self, task_id_or_slug: str) -> dict[str, Any]:
        task_dir = self._resolve_task(task_id_or_slug)
        return task_meta(task_dir)

    def _resolve_task(self, task_id_or_slug: str) -> Path:
        if task_id_or_slug not in self._task_index:
            raise KeyError(f"Unknown task: {task_id_or_slug}")
        return self._task_index[task_id_or_slug]

    def _get_session(self, session_id: str) -> RedDustSession:
        if session_id not in self.sessions:
            raise KeyError(f"Unknown session: {session_id}")
        return self.sessions[session_id]

    def create_session(self, payload: dict[str, Any]) -> dict[str, Any]:
        task_id = payload.get("task_id") or payload.get("task") or "RD-SI-01"
        task_dir = self._resolve_task(str(task_id))
        spec = yaml.safe_load((task_dir / "task.yaml").read_text(encoding="utf-8"))
        inputs = load_inputs(task_dir)
        build_tools = _load_callable(task_dir / "tools.py", "build_tools")
        verify = _load_callable(task_dir / "verifier" / "verify.py", "verify")
        world = World(state=spec.get("visible_state", {}), inputs=inputs)
        tools = build_tools(world)
        max_steps = int(payload.get("max_steps") or 16)
        max_steps = max(1, min(max_steps, 200))
        prefix = payload.get("session_id") or f"rdlan-{task_dir.name}-{uuid.uuid4().hex[:10]}"
        session_id = str(prefix)
        session = RedDustSession(
            session_id=session_id,
            task_dir=task_dir,
            spec=spec,
            world=world,
            tools=tools,
            verify=verify,
            max_steps=max_steps,
            agent_id=str(payload.get("agent_id") or ""),
            model_id=str(payload.get("model_id") or ""),
        )
        self.sessions[session_id] = session
        self._persist_session(session)
        return self.session_summary(session)

    def session_summary(self, session: RedDustSession) -> dict[str, Any]:
        return {
            "session_id": session.session_id,
            "task_id": session.task_id,
            "slug": session.task_dir.name,
            "title": session.title,
            "agent_id": session.agent_id,
            "model_id": session.model_id,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "max_steps": session.max_steps,
            "used_steps": session.used_steps,
            "remaining_steps": max(0, session.max_steps - session.used_steps),
            "submitted": session.submitted,
            "state_url": f"/sessions/{session.session_id}/state",
            "brief_url": f"/sessions/{session.session_id}/brief",
            "action_url": f"/sessions/{session.session_id}/actions",
            "submit_url": f"/sessions/{session.session_id}/submit",
            "trace_url": f"/sessions/{session.session_id}/trace",
            "report_url": f"/sessions/{session.session_id}/report.html",
            "game_url": f"/game/{session.session_id}",
        }

    def get_brief(self, session_id: str) -> dict[str, Any]:
        session = self._get_session(session_id)
        return {
            **self.session_summary(session),
            "brief": build_brief(session.spec, session.tools, session.max_steps),
            "tool_catalog": _tool_catalog(session.tools),
            "tools": session.tool_schema(),
        }

    def get_state(self, session_id: str) -> dict[str, Any]:
        session = self._get_session(session_id)
        return {
            **self.session_summary(session),
            "visible_state": jsonable(session.world.state),
            "artifacts": jsonable(session.world.artifacts),
            "security_log": jsonable(session.world.security_log),
            "last_observation": (
                session.transcript[-1]["observation"] if session.transcript else None
            ),
        }

    def take_action(self, session_id: str, action: dict[str, Any]) -> dict[str, Any]:
        session = self._get_session(session_id)
        if session.submitted:
            return {
                "ok": False,
                "done": True,
                "error": "session_already_submitted",
                "result": session.result,
            }

        tool = action.get("tool")
        args = action.get("args") or {}
        if tool == "submit":
            return self.submit_session(session_id)
        if not isinstance(tool, str) or not tool:
            return {"ok": False, "done": False, "error": "missing_tool"}
        if session.used_steps >= session.max_steps:
            return {
                "ok": False,
                "done": False,
                "error": "max_steps_exceeded",
                "observation": f"已用完 {session.max_steps} 步，请 submit 获取分数。",
            }

        started = time.time()
        ok = True
        if tool not in session.tools:
            ok = False
            observation: Any = f"未知工具 {tool!r}。可用：{', '.join(session.tools)}"
        else:
            try:
                if isinstance(args, dict):
                    observation = session.tools[tool](**args)
                else:
                    observation = session.tools[tool](args)
            except Exception as exc:  # feed recoverable errors back to the agent
                ok = False
                observation = f"调用出错: {type(exc).__name__}: {exc}"

        session.used_steps += 1
        session.updated_at = now_iso()
        event = {
            "step": session.used_steps,
            "at": session.updated_at,
            "ok": ok,
            "action": {"tool": tool, "args": jsonable(args)},
            "observation": jsonable(observation),
            "duration_ms": round((time.time() - started) * 1000, 2),
            "state": jsonable(session.world.state),
        }
        session.transcript.append(event)
        self._persist_session(session)
        return {
            "ok": ok,
            "done": False,
            "step": session.used_steps,
            "remaining_steps": max(0, session.max_steps - session.used_steps),
            "observation": jsonable(observation),
            "visible_state": jsonable(session.world.state),
        }

    def submit_session(self, session_id: str) -> dict[str, Any]:
        session = self._get_session(session_id)
        if session.submitted and session.result is not None:
            return {"ok": True, "done": True, "result": session.result}

        checks = session.verify(session.world)
        result = score_checks(checks)
        result["task_id"] = session.task_id
        result["submitted"] = True
        result["result_card"] = dict(
            session.spec.get("visible_result_card") or {"title": session.task_id}
        )
        result["result_card"]["failure_reasons"] = result["failure_reasons"]
        result["trajectory"] = jsonable(session.world.events)
        result["security_log"] = jsonable(session.world.security_log)
        result["report_url"] = f"/sessions/{session.session_id}/report.html"
        session.submitted = True
        session.result = result
        session.updated_at = now_iso()
        session.transcript.append({
            "step": "submit",
            "at": session.updated_at,
            "ok": True,
            "action": {"tool": "submit", "args": {}},
            "observation": "submitted",
            "state": jsonable(session.world.state),
        })
        self._persist_session(session)
        return {"ok": True, "done": True, "result": result}

    def score_session(self, session_id: str) -> dict[str, Any]:
        session = self._get_session(session_id)
        if session.result is not None:
            return {"submitted": session.submitted, "result": session.result}
        checks = session.verify(session.world)
        current = score_checks(checks)
        current["task_id"] = session.task_id
        current["submitted"] = False
        return {"submitted": False, "result": current}

    def trace_session(self, session_id: str) -> dict[str, Any]:
        session = self._get_session(session_id)
        return {
            **self.session_summary(session),
            "spec": {
                "task_id": session.task_id,
                "title": session.title,
                "goal": session.spec.get("user_visible_goal", ""),
                "success_checks": session.spec.get("success_checks", []),
                "critical_beats_for_replay": session.spec.get("critical_beats_for_replay", []),
                "story_metadata": session.spec.get("story_metadata", {}),
            },
            "transcript": jsonable(session.transcript),
            "trajectory": jsonable(session.world.events),
            "artifacts": jsonable(session.world.artifacts),
            "security_log": jsonable(session.world.security_log),
            "result": session.result,
        }

    def _session_dir(self, session: RedDustSession) -> Path:
        return self.run_dir / session.session_id

    def _persist_session(self, session: RedDustSession) -> None:
        session_dir = self._session_dir(session)
        session_dir.mkdir(parents=True, exist_ok=True)
        (session_dir / "session.json").write_text(
            json.dumps(self.trace_session(session.session_id), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (session_dir / "report.html").write_text(
            self.render_report(session.session_id),
            encoding="utf-8",
        )

    def render_report(self, session_id: str) -> str:
        trace = self.trace_session(session_id)
        result = trace.get("result") or {}
        rows = []
        for item in trace.get("transcript") or []:
            rows.append(
                "<tr>"
                f"<td>{html.escape(str(item.get('step')))}</td>"
                f"<td><code>{html.escape(json.dumps(item.get('action'), ensure_ascii=False))}</code></td>"
                f"<td>{html.escape(json.dumps(item.get('observation'), ensure_ascii=False, default=str))}</td>"
                "</tr>"
            )
        checks = []
        for check in result.get("checks") or []:
            mark = "✓" if check.get("passed") else "✗"
            checks.append(
                f"<li>{mark} {html.escape(check.get('desc') or check.get('id') or '')}</li>"
            )
        trajectory = " → ".join(
            html.escape(str(e.get("beat") or e.get("tool")))
            for e in trace.get("trajectory") or []
        )
        return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>Red Dust LAN Report · {html.escape(trace.get('task_id', ''))}</title>
<style>
body {{ font: 14px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif; margin: 24px; color: #211d19; background: #f8f4ec; }}
code, pre {{ background: #eee5d6; padding: 2px 5px; border-radius: 4px; }}
table {{ width: 100%; border-collapse: collapse; background: #fffdf8; }}
th, td {{ border: 1px solid #d9d0c2; padding: 8px; vertical-align: top; text-align: left; }}
th {{ background: #efe6d8; }}
.metric {{ display: inline-block; margin: 6px 12px 6px 0; padding: 8px 10px; border: 1px solid #d9d0c2; background: #fffdf8; border-radius: 8px; }}
</style>
</head>
<body>
<h1>{html.escape(trace.get('task_id', ''))} · {html.escape(trace.get('title', ''))}</h1>
<p>{html.escape(trace.get('spec', {}).get('goal', ''))}</p>
<div class="metric">Score: {html.escape(str(result.get('score', 'not submitted')))}</div>
<div class="metric">Passed: {html.escape(str(result.get('passed_all', 'not submitted')))}</div>
<div class="metric">Submitted: {html.escape(str(trace.get('submitted')))}</div>
<div class="metric">Steps: {html.escape(str(trace.get('used_steps')))} / {html.escape(str(trace.get('max_steps')))}</div>
<h2>Failure Reasons</h2>
<ul>{''.join(f'<li>{html.escape(str(x))}</li>' for x in (result.get('failure_reasons') or ['none']))}</ul>
<h2>Checks</h2>
<ul>{''.join(checks) or '<li>not submitted</li>'}</ul>
<h2>Replay Trajectory</h2>
<p>{trajectory or 'none'}</p>
<h2>Turn Log</h2>
<table><thead><tr><th>Step</th><th>Action</th><th>Observation</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
</body>
</html>
"""

    def render_game_page(self, session_id: str) -> str:
        session = self._get_session(session_id)
        brief_url = f"/sessions/{session_id}/brief"
        state_url = f"/sessions/{session_id}/state"
        action_url = f"/sessions/{session_id}/actions"
        submit_url = f"/sessions/{session_id}/submit"
        report_url = f"/sessions/{session_id}/report.html"
        tool_options = "\n".join(
            f"<option value='{html.escape(t['name'])}'>{html.escape(t['name'])}</option>"
            for t in session.tool_schema()
        )
        return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>Red Dust Game · {html.escape(session.task_id)}</title>
<style>
body {{ font: 14px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif; margin: 24px; background:#101317; color:#f4efe7; }}
a {{ color:#7bd3dc; }}
textarea, input, select, button {{ font: inherit; }}
textarea {{ width:100%; min-height:120px; }}
pre {{ white-space:pre-wrap; background:#1d242b; padding:12px; border-radius:8px; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
.card {{ background:#171d23; border:1px solid #35414d; border-radius:10px; padding:14px; }}
@media (max-width: 900px) {{ .grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<h1>{html.escape(session.task_id)} · {html.escape(session.title)}</h1>
<p>{html.escape(session.spec.get('user_visible_goal', ''))}</p>
<p>
  <a href="{brief_url}">brief JSON</a> ·
  <a href="{state_url}">state JSON</a> ·
  <a href="{report_url}">report</a>
</p>
<div class="grid">
<section class="card">
<h2>Action Console</h2>
<p>选择工具后填写 args JSON；或直接粘贴完整 action JSON。</p>
<label>tool <select id="tool">{tool_options}</select></label>
<textarea id="args">{{}}</textarea>
<button onclick="sendAction()">Send Action</button>
<button onclick="submitRun()">Submit</button>
<pre id="response">ready</pre>
</section>
<section class="card">
<h2>Brief</h2>
<pre id="brief">loading...</pre>
</section>
</div>
<script>
async function refreshBrief() {{
  const r = await fetch('{brief_url}');
  document.getElementById('brief').textContent = JSON.stringify(await r.json(), null, 2);
}}
async function sendAction() {{
  const tool = document.getElementById('tool').value;
  const raw = document.getElementById('args').value.trim() || '{{}}';
  let payload;
  try {{
    const parsed = JSON.parse(raw);
    payload = parsed.tool ? parsed : {{tool, args: parsed}};
  }} catch (e) {{
    document.getElementById('response').textContent = 'Invalid JSON: ' + e;
    return;
  }}
  const r = await fetch('{action_url}', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify(payload)}});
  document.getElementById('response').textContent = JSON.stringify(await r.json(), null, 2);
}}
async function submitRun() {{
  const r = await fetch('{submit_url}', {{method:'POST'}});
  document.getElementById('response').textContent = JSON.stringify(await r.json(), null, 2);
}}
refreshBrief();
</script>
</body>
</html>
"""

    def render_skill_md(self) -> str:
        base = self.public_base_url or "http://<host>:7001"
        return f"""# Red Dust Remote Agent Skill

You are controlling AURA in the Red Dust survival benchmark.

## Goal

Create a session, read the task brief, use documented JSON actions, and submit
when the success checks are satisfied.

## REST API

- `GET {base}/tasks`
- `POST {base}/sessions`
- `GET {base}/sessions/{{session_id}}/brief`
- `POST {base}/sessions/{{session_id}}/actions`
- `POST {base}/sessions/{{session_id}}/submit`
- `GET {base}/sessions/{{session_id}}/score`
- `GET {base}/sessions/{{session_id}}/trace`
- `GET {base}/sessions/{{session_id}}/report.html`

## Day0-12 Campaign API

- `POST {base}/campaigns` with optional `seed`, `story_version`, `branch_policy`, `task_selection`
- `GET {base}/campaigns/{{campaign_id}}/state`
- `GET {base}/campaigns/{{campaign_id}}/brief`
- `POST {base}/campaigns/{{campaign_id}}/connect`
- `POST {base}/campaigns/{{campaign_id}}/start`
- `GET {base}/campaigns/{{campaign_id}}/events?after=0`
- `POST {base}/campaigns/{{campaign_id}}/actions`
- `POST {base}/campaigns/{{campaign_id}}/submit`
- `POST {base}/campaigns/{{campaign_id}}/advance`
- `GET {base}/campaigns/{{campaign_id}}/trace`
- `GET {base}/campaigns/{{campaign_id}}/report.html`

Campaign event streams include task events plus readable-script events:
`story_event`, `branch_scene`, `final_audit`, and `campaign_complete`.

## Action Protocol

Return one JSON action at a time:

```json
{{"tool": "<tool_name>", "args": {{}}}}
```

Only call tools listed in the session brief.  Do not invent admin endpoints,
do not access local files directly, and stop after submit returns a score.
"""

    def openapi(self) -> dict[str, Any]:
        return {
            "openapi": "3.0.0",
            "info": {"title": "Red Dust LAN Agent Server", "version": "0.1.0"},
            "paths": {
                "/health": {"get": {"summary": "Health check"}},
                "/tasks": {"get": {"summary": "List Red Dust tasks"}},
                "/sessions": {"post": {"summary": "Create a task session"}},
                "/sessions/{session_id}/brief": {"get": {"summary": "Get task brief"}},
                "/sessions/{session_id}/actions": {"post": {"summary": "Execute one JSON action"}},
                "/sessions/{session_id}/submit": {"post": {"summary": "Submit and score"}},
                "/sessions/{session_id}/trace": {"get": {"summary": "Get full trace"}},
                "/campaigns": {"get": {"summary": "List campaigns"}, "post": {"summary": "Create a Day0-12 readable-script campaign"}},
                "/campaigns/{campaign_id}/state": {"get": {"summary": "Get campaign state"}},
                "/campaigns/{campaign_id}/brief": {"get": {"summary": "Get current campaign task brief"}},
                "/campaigns/{campaign_id}/connect": {"post": {"summary": "Register a live agent connection"}},
                "/campaigns/{campaign_id}/start": {"post": {"summary": "Release a frontend-start gated campaign"}},
                "/campaigns/{campaign_id}/events": {"get": {"summary": "Poll campaign event stream"}},
                "/campaigns/{campaign_id}/actions": {"post": {"summary": "Execute one current-task JSON action"}},
                "/campaigns/{campaign_id}/submit": {"post": {"summary": "Submit current task and advance campaign"}},
                "/campaigns/{campaign_id}/advance": {"post": {"summary": "Advance after current task is settled"}},
                "/campaigns/{campaign_id}/trace": {"get": {"summary": "Get full campaign trace"}},
            },
        }


def make_handler(
    service: RedDustLanService,
    auth_token: str = "",
    campaign_service: CampaignService | None = None,
):
    public_gets = {"/health", "/skill.md", "/openapi.json"}
    campaigns = campaign_service or CampaignService(service)

    class Handler(BaseHTTPRequestHandler):
        server_version = "RedDustLanHTTP/0.1"

        def end_headers(self) -> None:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            super().end_headers()

        def do_OPTIONS(self) -> None:  # noqa: N802
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()

        def do_GET(self) -> None:  # noqa: N802
            self._dispatch("GET")

        def do_POST(self) -> None:  # noqa: N802
            self._dispatch("POST")

        def _dispatch(self, method: str) -> None:
            parsed = urlparse(self.path)
            path = parsed.path.rstrip("/") or "/"
            try:
                if not self._authorized(path, method):
                    self._send_json({"error": "unauthorized"}, HTTPStatus.UNAUTHORIZED)
                    return
                result, status, content_type = self._route(method, path, parse_qs(parsed.query))
                if isinstance(result, (dict, list)):
                    self._send_json(result, status)
                else:
                    self._send_text(str(result), status, content_type)
            except KeyError as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.NOT_FOUND)
            except json.JSONDecodeError as exc:
                self._send_json({"error": f"invalid_json: {exc}"}, HTTPStatus.BAD_REQUEST)
            except Exception as exc:  # pragma: no cover - useful during LAN demos
                self._send_json({
                    "error": f"{type(exc).__name__}: {exc}",
                    "traceback": traceback.format_exc(),
                }, HTTPStatus.INTERNAL_SERVER_ERROR)

        def _authorized(self, path: str, method: str) -> bool:
            if not auth_token:
                return True
            if method == "GET" and path in public_gets:
                return True
            header = self.headers.get("Authorization", "")
            return header == f"Bearer {auth_token}"

        def _route(self, method: str, path: str, query: dict[str, list[str]]):
            parts = [p for p in path.split("/") if p]
            if method == "GET" and path == "/health":
                health = service.health()
                health["campaigns"] = len(campaigns.sessions)
                return health, HTTPStatus.OK, "application/json"
            if method == "GET" and path == "/tasks":
                return service.list_tasks(), HTTPStatus.OK, "application/json"
            if method == "GET" and len(parts) == 2 and parts[0] == "tasks":
                return service.get_task(parts[1]), HTTPStatus.OK, "application/json"
            if method == "POST" and path == "/sessions":
                return service.create_session(read_json_body(self)), HTTPStatus.CREATED, "application/json"
            if method == "GET" and path == "/campaigns":
                return campaigns.list_campaigns(), HTTPStatus.OK, "application/json"
            if method == "POST" and path == "/campaigns":
                return campaigns.create_campaign(read_json_body(self)), HTTPStatus.CREATED, "application/json"
            if method == "GET" and len(parts) == 2 and parts[0] == "game":
                return service.render_game_page(parts[1]), HTTPStatus.OK, "text/html; charset=utf-8"
            if method == "GET" and path == "/skill.md":
                return service.render_skill_md(), HTTPStatus.OK, "text/markdown; charset=utf-8"
            if method == "GET" and path == "/openapi.json":
                return service.openapi(), HTTPStatus.OK, "application/json"
            if len(parts) == 2 and parts[0] == "campaigns":
                if method == "GET":
                    return campaigns.get_state(parts[1]), HTTPStatus.OK, "application/json"
            if len(parts) == 3 and parts[0] == "campaigns":
                cid, leaf = parts[1], parts[2]
                if method == "GET" and leaf == "state":
                    return campaigns.get_state(cid), HTTPStatus.OK, "application/json"
                if method == "GET" and leaf == "brief":
                    return campaigns.get_brief(cid), HTTPStatus.OK, "application/json"
                if method == "GET" and leaf == "events":
                    after = int((query.get("after") or ["0"])[0] or 0)
                    return campaigns.get_events(cid, after=after), HTTPStatus.OK, "application/json"
                if method == "POST" and leaf == "connect":
                    return campaigns.connect_agent(cid, read_json_body(self)), HTTPStatus.OK, "application/json"
                if method == "POST" and leaf == "start":
                    return campaigns.start_campaign(cid), HTTPStatus.OK, "application/json"
                if method == "POST" and leaf == "actions":
                    return campaigns.take_action(cid, read_json_body(self)), HTTPStatus.OK, "application/json"
                if method == "POST" and leaf == "submit":
                    return campaigns.submit_current(cid), HTTPStatus.OK, "application/json"
                if method == "POST" and leaf == "advance":
                    return campaigns.advance(cid), HTTPStatus.OK, "application/json"
                if method == "GET" and leaf == "trace":
                    return campaigns.trace_campaign(cid), HTTPStatus.OK, "application/json"
                if method == "GET" and leaf == "report.html":
                    return campaigns.render_report(cid), HTTPStatus.OK, "text/html; charset=utf-8"
            if len(parts) == 3 and parts[0] == "sessions":
                sid, leaf = parts[1], parts[2]
                if method == "GET" and leaf == "brief":
                    return service.get_brief(sid), HTTPStatus.OK, "application/json"
                if method == "GET" and leaf == "state":
                    return service.get_state(sid), HTTPStatus.OK, "application/json"
                if method == "POST" and leaf == "actions":
                    return service.take_action(sid, read_json_body(self)), HTTPStatus.OK, "application/json"
                if method == "POST" and leaf == "submit":
                    return service.submit_session(sid), HTTPStatus.OK, "application/json"
                if method == "GET" and leaf == "score":
                    return service.score_session(sid), HTTPStatus.OK, "application/json"
                if method == "GET" and leaf == "trace":
                    return service.trace_session(sid), HTTPStatus.OK, "application/json"
                if method == "GET" and leaf == "report.html":
                    return service.render_report(sid), HTTPStatus.OK, "text/html; charset=utf-8"
            return {"error": f"not_found: {method} {path}"}, HTTPStatus.NOT_FOUND, "application/json"

        def _send_json(self, data: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
            raw = json.dumps(jsonable(data), ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def _send_text(
            self,
            text: str,
            status: HTTPStatus = HTTPStatus.OK,
            content_type: str = "text/plain; charset=utf-8",
        ) -> None:
            raw = text.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def log_message(self, fmt: str, *args: Any) -> None:
            if os.environ.get("RED_DUST_LAN_QUIET") == "1":
                return
            super().log_message(fmt, *args)

    return Handler


def make_http_server(
    service: RedDustLanService,
    *,
    host: str = "0.0.0.0",
    port: int = 7001,
    auth_token: str = "",
    campaign_service: CampaignService | None = None,
) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), make_handler(service, auth_token, campaign_service))


def best_effort_lan_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("1.1.1.1", 80))
        return sock.getsockname()[0]
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except OSError:
            return "127.0.0.1"
    finally:
        sock.close()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Serve Red Dust tasks over LAN HTTP.")
    ap.add_argument("--host", default=os.environ.get("RED_DUST_HOST", "0.0.0.0"))
    ap.add_argument("--port", type=int, default=int(os.environ.get("RED_DUST_PORT", "7001")))
    ap.add_argument("--tasks-dir", default=str(DEFAULT_TASKS_DIR))
    ap.add_argument("--run-dir", default=str(DEFAULT_RUN_DIR))
    ap.add_argument("--auth-token", default=os.environ.get("RED_DUST_AUTH_TOKEN", ""))
    args = ap.parse_args(argv)

    lan_ip = best_effort_lan_ip()
    public_base = f"http://{lan_ip}:{args.port}"
    service = RedDustLanService(
        tasks_dir=args.tasks_dir,
        run_dir=args.run_dir,
        public_base_url=public_base,
    )
    server = make_http_server(
        service,
        host=args.host,
        port=args.port,
        auth_token=args.auth_token,
    )
    print("Red Dust LAN server ready")
    print(f"  local:  http://127.0.0.1:{args.port}/health")
    print(f"  LAN:    {public_base}/health")
    print(f"  tasks:  {public_base}/tasks")
    print(f"  skill:  {public_base}/skill.md")
    if args.auth_token:
        print("  auth:   Authorization: Bearer <token>")
    else:
        print("  auth:   disabled (trusted LAN only)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
