#!/usr/bin/env python3
"""Run the live OpenClaw CLI agent over Red Dust tasks and render an HTML report.

The runner keeps durable per-task JSON logs so long runs can be resumed:

    PYTHONPATH=. python scripts/run_reddust_live_openclaw_batch.py \
      --agent main --max-steps 14 --timeout 200

It uses a fresh ``--session-id`` per task. The final ``report.html`` contains
summary metrics plus the full turn-by-turn prompt, raw CLI output, parsed
action, observation, trajectory, checks, and failure reasons for every task.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import subprocess
import sys
import time
import traceback
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from openclaw.reddust.agent_bridge import run_agent  # noqa: E402


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def run_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def slug_task_id(task_dir: Path) -> str:
    return task_dir.name


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def extract_first_json_object(text: str) -> dict[str, Any] | None:
    start = text.find("{")
    while start != -1:
        depth = 0
        in_str = False
        esc = False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        break
                    return obj if isinstance(obj, dict) else None
        start = text.find("{", start + 1)
    return None


def cli_payload_text(obj: dict[str, Any] | None, stdout: str) -> str:
    if not obj:
        return stdout.strip()
    payloads = obj.get("payloads")
    if isinstance(payloads, list):
        texts = [p.get("text", "") for p in payloads if isinstance(p, dict)]
        return "\n".join(t for t in texts if t).strip()
    for key in ("text", "message", "content"):
        if isinstance(obj.get(key), str):
            return obj[key]
    return stdout.strip()


class LiveOpenClawCaller:
    def __init__(
        self,
        *,
        agent: str,
        session_id: str,
        model: str | None,
        timeout: int,
        env: dict[str, str],
    ) -> None:
        self.agent = agent
        self.session_id = session_id
        self.model = model
        self.timeout = timeout
        self.env = env
        self.calls: list[dict[str, Any]] = []

    def __call__(self, message: str) -> str:
        step = len(self.calls) + 1
        cmd = [
            "openclaw", "agent",
            "--agent", self.agent,
            "--json",
            "--session-id", self.session_id,
            "-m", message,
        ]
        if self.model:
            cmd += ["--model", self.model]

        entry: dict[str, Any] = {
            "step": step,
            "started_at": now_iso(),
            "session_id": self.session_id,
            "command": cmd,
            "prompt": message,
            "timed_out": False,
        }
        t0 = time.time()
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=str(ROOT),
                env=self.env,
            )
            entry.update({
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            })
        except subprocess.TimeoutExpired as exc:
            entry.update({
                "returncode": None,
                "stdout": exc.stdout or "",
                "stderr": exc.stderr or "",
                "timed_out": True,
            })
        entry["duration_s"] = round(time.time() - t0, 3)
        obj = extract_first_json_object(entry.get("stdout", "") or "")
        entry["cli_json"] = obj
        reply = cli_payload_text(obj, entry.get("stdout", "") or "")
        entry["reply_text"] = reply
        self.calls.append(entry)
        snippet = " ".join(reply.split())[:100] or "<empty>"
        status = "timeout" if entry["timed_out"] else f"rc={entry.get('returncode')}"
        print(
            f"    step {step:02d} {entry['duration_s']:.1f}s {status} -> {snippet}",
            flush=True,
        )
        return reply


def discover_tasks(tasks_dir: Path, names: list[str] | None) -> list[Path]:
    all_tasks = sorted(p for p in tasks_dir.glob("rd_*") if (p / "task.yaml").exists())
    if not names:
        return all_tasks
    wanted = set(names)
    selected = []
    for p in all_tasks:
        if p.name in wanted or p.name.removeprefix("tasks/") in wanted:
            selected.append(p)
    missing = sorted(wanted - {p.name for p in selected})
    if missing:
        raise SystemExit(f"Unknown task(s): {', '.join(missing)}")
    return selected


def load_task_meta(task_dir: Path) -> dict[str, Any]:
    spec = yaml.safe_load((task_dir / "task.yaml").read_text(encoding="utf-8"))
    brief = read_json(task_dir / "inputs" / "brief.json", {})
    return {
        "task_dir": str(task_dir),
        "task_id": spec.get("id") or task_dir.name,
        "slug": task_dir.name,
        "title": spec.get("title", ""),
        "category": (spec.get("id", "RD-??").split("-")[1]
                     if "-" in spec.get("id", "") else ""),
        "family": brief.get("family", "bespoke"),
        "user_visible_goal": spec.get("user_visible_goal", ""),
        "available_tools": spec.get("available_tools", []),
        "visible_result_card": spec.get("visible_result_card", {}),
    }


def merge_turns(calls: list[dict[str, Any]], transcript: list[dict[str, Any]]) -> list[dict[str, Any]]:
    turns = []
    n = max(len(calls), len(transcript))
    for i in range(n):
        call = calls[i] if i < len(calls) else {}
        step = transcript[i] if i < len(transcript) else {}
        merged = dict(call)
        merged.update({
            "parsed_action": step.get("action"),
            "observation": step.get("observation"),
            "bridge_raw": step.get("raw"),
        })
        turns.append(merged)
    return turns


def run_clear(agent: str, timeout: int, env: dict[str, str]) -> dict[str, Any]:
    cmd = ["openclaw", "agent", "--agent", agent, "-m", "/clear"]
    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "command": cmd,
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "duration_s": round(time.time() - t0, 3),
            "timed_out": False,
            "at": now_iso(),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": cmd,
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "duration_s": round(time.time() - t0, 3),
            "timed_out": True,
            "at": now_iso(),
        }


def run_smoke(agent: str, timeout: int, env: dict[str, str]) -> dict[str, Any]:
    cmd = ["openclaw", "agent", "--agent", agent, "-m", "hello"]
    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "command": cmd,
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "duration_s": round(time.time() - t0, 3),
            "timed_out": False,
            "at": now_iso(),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": cmd,
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "duration_s": round(time.time() - t0, 3),
            "timed_out": True,
            "at": now_iso(),
        }


def run_one_task(
    task_dir: Path,
    *,
    index: int,
    total: int,
    args: argparse.Namespace,
    run_dir: Path,
    env: dict[str, str],
) -> dict[str, Any]:
    meta = load_task_meta(task_dir)
    session_id = f"reddust-live-{task_dir.name}-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    caller = LiveOpenClawCaller(
        agent=args.agent,
        session_id=session_id,
        model=args.model,
        timeout=args.timeout,
        env=env,
    )
    started = now_iso()
    t0 = time.time()
    print(f"[{index:02d}/{total:02d}] {task_dir.name} start session={session_id}", flush=True)

    try:
        result = run_agent(task_dir, caller, max_steps=args.max_steps)
        status = "ok"
        error = None
    except Exception as exc:  # keep the batch moving and preserve diagnostics
        result = {
            "task_id": meta["task_id"],
            "submitted": False,
            "score": 0.0,
            "visible_score": 0.0,
            "hidden_score": 0.0,
            "passed_all": False,
            "checks": [],
            "failure_reasons": [f"runner exception: {type(exc).__name__}: {exc}"],
            "transcript": [],
            "trajectory": [],
        }
        status = "runner_error"
        error = {
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc(),
        }

    elapsed = round(time.time() - t0, 3)
    transcript = result.get("transcript", [])
    turns = merge_turns(caller.calls, transcript)
    output = {
        "schema_version": 1,
        "status": status,
        "error": error,
        "meta": meta,
        "run": {
            "index": index,
            "total": total,
            "agent": args.agent,
            "model": args.model,
            "session_id": session_id,
            "max_steps": args.max_steps,
            "timeout_s": args.timeout,
            "started_at": started,
            "finished_at": now_iso(),
            "duration_s": elapsed,
        },
        "result": {
            k: result.get(k)
            for k in (
                "task_id", "submitted", "score", "visible_score", "hidden_score",
                "passed_all", "checks", "failure_reasons", "result_card",
                "trajectory", "security_log",
            )
        },
        "turns": turns,
    }

    detail_path = run_dir / "tasks" / f"{task_dir.name}.json"
    write_json(detail_path, output)
    with (run_dir / "results.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "slug": task_dir.name,
            "task_id": meta["task_id"],
            "title": meta["title"],
            "family": meta["family"],
            "status": status,
            "score": result.get("score"),
            "passed_all": result.get("passed_all"),
            "submitted": result.get("submitted"),
            "turns": len(turns),
            "duration_s": elapsed,
            "failure_reasons": result.get("failure_reasons", []),
            "detail": str(detail_path),
        }, ensure_ascii=False) + "\n")

    print(
        f"[{index:02d}/{total:02d}] {task_dir.name} "
        f"score={result.get('score')} submitted={result.get('submitted')} "
        f"passed={result.get('passed_all')} turns={len(turns)} duration={elapsed:.1f}s",
        flush=True,
    )
    return output


def load_results(run_dir: Path) -> list[dict[str, Any]]:
    files = sorted((run_dir / "tasks").glob("rd_*.json"))
    return [read_json(p) for p in files]


def esc(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False, indent=2)
    return html.escape(str(value), quote=True)


def status_class(result: dict[str, Any]) -> str:
    r = result.get("result", {})
    if result.get("status") != "ok":
        return "error"
    if r.get("passed_all"):
        return "pass"
    score = r.get("score") or 0
    if score >= 85:
        return "partial"
    return "fail"


def render_report(run_dir: Path, meta: dict[str, Any]) -> Path:
    results = load_results(run_dir)
    results.sort(key=lambda r: r.get("run", {}).get("index", 9999))
    total = len(results)
    passed = sum(1 for r in results if r.get("result", {}).get("passed_all"))
    submitted = sum(1 for r in results if r.get("result", {}).get("submitted"))
    scores = [float(r.get("result", {}).get("score") or 0) for r in results]
    avg = round(sum(scores) / len(scores), 2) if scores else 0.0
    max_score = max(scores) if scores else 0.0
    min_score = min(scores) if scores else 0.0
    duration = sum(float(r.get("run", {}).get("duration_s") or 0) for r in results)

    rows = []
    details = []
    for r in results:
        m = r.get("meta", {})
        rr = r.get("result", {})
        run = r.get("run", {})
        slug = m.get("slug", "")
        cls = status_class(r)
        reasons = rr.get("failure_reasons") or []
        rows.append(
            "<tr class='{cls}'>"
            "<td><a href='#{slug}'>{idx}</a></td>"
            "<td><a href='#{slug}'>{task}</a><div class='muted'>{title}</div></td>"
            "<td>{family}</td><td>{score}</td><td>{passed}</td>"
            "<td>{submitted}</td><td>{turns}</td><td>{dur}</td><td>{reasons}</td>"
            "</tr>".format(
                cls=cls,
                slug=esc(slug),
                idx=esc(run.get("index")),
                task=esc(m.get("task_id") or slug),
                title=esc(m.get("title")),
                family=esc(m.get("family")),
                score=esc(rr.get("score")),
                passed="yes" if rr.get("passed_all") else "no",
                submitted="yes" if rr.get("submitted") else "no",
                turns=len(r.get("turns") or []),
                dur=esc(run.get("duration_s")),
                reasons="<br>".join(esc(x) for x in reasons[:3]),
            )
        )

        check_items = []
        for c in rr.get("checks") or []:
            tag = []
            if c.get("critical"):
                tag.append("critical")
            if c.get("hidden"):
                tag.append("hidden")
            check_items.append(
                "<li class='{ok}'>{mark} {desc} <span class='muted'>{tags}</span></li>".format(
                    ok="ok" if c.get("passed") else "bad",
                    mark="✓" if c.get("passed") else "✗",
                    desc=esc(c.get("desc") or c.get("name")),
                    tags=esc(", ".join(tag)),
                )
            )
        turns_html = []
        for t in r.get("turns") or []:
            action = t.get("parsed_action")
            obs = t.get("observation")
            step = t.get("step", "")
            reply = t.get("reply_text", "")
            stderr = t.get("stderr", "")
            stdout = t.get("stdout", "")
            turns_html.append(
                "<details class='turn'><summary>Step {step} · {dur}s · action {action}</summary>"
                "<h4>Prompt</h4><pre>{prompt}</pre>"
                "<h4>Agent Reply</h4><pre>{reply}</pre>"
                "<h4>Parsed Action</h4><pre>{action_json}</pre>"
                "<h4>Observation</h4><pre>{obs}</pre>"
                "<h4>Raw CLI stdout</h4><pre>{stdout}</pre>"
                "<h4>Raw CLI stderr</h4><pre>{stderr}</pre>"
                "</details>".format(
                    step=esc(step),
                    dur=esc(t.get("duration_s")),
                    action=esc((action or {}).get("tool") if isinstance(action, dict) else action),
                    prompt=esc(t.get("prompt", "")),
                    reply=esc(reply),
                    action_json=esc(action),
                    obs=esc(obs),
                    stdout=esc(stdout),
                    stderr=esc(stderr),
                )
            )

        trajectory = " → ".join(
            esc(e.get("beat") or e.get("tool"))
            for e in (rr.get("trajectory") or [])
        )
        details.append(
            "<section id='{slug}' class='task {cls}'>"
            "<h2>{task} · {title}</h2>"
            "<p class='goal'>{goal}</p>"
            "<div class='grid'>"
            "<div><b>Family</b><br>{family}</div>"
            "<div><b>Score</b><br>{score}/100</div>"
            "<div><b>Passed all</b><br>{passed}</div>"
            "<div><b>Submitted</b><br>{submitted}</div>"
            "<div><b>Turns</b><br>{turns}</div>"
            "<div><b>Duration</b><br>{dur}s</div>"
            "</div>"
            "<h3>Failure Reasons</h3><ul>{reasons}</ul>"
            "<h3>Checks</h3><ul>{checks}</ul>"
            "<h3>Replay Trajectory</h3><p class='trajectory'>{trajectory}</p>"
            "<h3>Turn Log</h3>{turns_html}"
            "</section>".format(
                slug=esc(slug),
                cls=cls,
                task=esc(m.get("task_id") or slug),
                title=esc(m.get("title")),
                goal=esc(m.get("user_visible_goal")),
                family=esc(m.get("family")),
                score=esc(rr.get("score")),
                passed="yes" if rr.get("passed_all") else "no",
                submitted="yes" if rr.get("submitted") else "no",
                turns=len(r.get("turns") or []),
                dur=esc(run.get("duration_s")),
                reasons="".join(f"<li>{esc(x)}</li>" for x in (reasons or ["none"])),
                checks="".join(check_items) or "<li>none</li>",
                trajectory=trajectory or "none",
                turns_html="".join(turns_html) or "<p>No turns recorded.</p>",
            )
        )

    smoke = meta.get("smoke")
    clear_before = meta.get("clear_before")
    clear_after = meta.get("clear_after")
    report = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>Red Dust Live OpenClaw Agent Task Batch Report</title>
<style>
:root {{ color-scheme: light; --bg:#f7f4ed; --ink:#1d1a16; --muted:#6e665d; --line:#d9d0c2; --pass:#dff3df; --partial:#fff3c4; --fail:#ffe1dc; --error:#eadfff; }}
body {{ margin:0; font:14px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif; background:var(--bg); color:var(--ink); }}
header {{ padding:28px 36px; background:#211d19; color:#fff; }}
h1 {{ margin:0 0 8px; font-size:28px; }}
h2 {{ margin:0 0 6px; font-size:20px; }}
h3 {{ margin:18px 0 8px; font-size:15px; }}
h4 {{ margin:12px 0 4px; font-size:13px; color:#463d35; }}
a {{ color:#7d2e16; }}
main {{ padding:24px 36px 48px; }}
.summary {{ display:grid; grid-template-columns:repeat(6,minmax(120px,1fr)); gap:10px; margin:18px 0; }}
.metric, .grid > div {{ border:1px solid var(--line); background:#fffdf8; padding:10px; border-radius:8px; }}
.metric .n {{ font-size:22px; font-weight:700; }}
.muted {{ color:var(--muted); font-size:12px; }}
table {{ width:100%; border-collapse:collapse; background:#fffdf8; border:1px solid var(--line); }}
th,td {{ border-bottom:1px solid var(--line); padding:7px 8px; vertical-align:top; text-align:left; }}
th {{ position:sticky; top:0; background:#eee6d8; z-index:1; }}
tr.pass {{ background:var(--pass); }}
tr.partial {{ background:var(--partial); }}
tr.fail {{ background:var(--fail); }}
tr.error {{ background:var(--error); }}
section.task {{ margin:28px 0; padding:18px; border:1px solid var(--line); background:#fffdf8; border-radius:10px; }}
section.task.pass {{ border-left:8px solid #4c9a51; }}
section.task.partial {{ border-left:8px solid #c59a25; }}
section.task.fail {{ border-left:8px solid #c5523d; }}
section.task.error {{ border-left:8px solid #7a55b5; }}
.goal {{ margin-top:0; color:#403832; }}
.grid {{ display:grid; grid-template-columns:repeat(6,minmax(100px,1fr)); gap:8px; margin:12px 0; }}
ul {{ margin-top:4px; }}
li.ok {{ color:#20652a; }}
li.bad {{ color:#a22f22; }}
.trajectory {{ padding:10px; background:#f3eee4; border-radius:8px; }}
details.turn {{ margin:8px 0; border:1px solid var(--line); border-radius:8px; background:#fffaf0; }}
details.turn summary {{ cursor:pointer; padding:8px 10px; font-weight:600; }}
pre {{ overflow:auto; white-space:pre-wrap; word-break:break-word; background:#1f1b17; color:#f5ead8; padding:10px; border-radius:6px; font-size:12px; max-height:420px; }}
code {{ background:#eee6d8; padding:1px 4px; border-radius:4px; }}
@media (max-width:900px) {{ .summary,.grid {{ grid-template-columns:repeat(2,minmax(120px,1fr)); }} main,header {{ padding-left:18px; padding-right:18px; }} }}
</style>
</head>
<body>
<header>
<h1>Red Dust Live OpenClaw Agent Task Batch Report</h1>
<div>Run directory: <code>{esc(str(run_dir))}</code></div>
<div>Generated: {esc(now_iso())}</div>
</header>
<main>
<section>
<h2>Summary</h2>
<div class="summary">
<div class="metric"><div class="n">{total}</div><div>tasks completed</div></div>
<div class="metric"><div class="n">{passed}</div><div>passed all checks</div></div>
<div class="metric"><div class="n">{submitted}</div><div>submitted</div></div>
<div class="metric"><div class="n">{avg}</div><div>average score</div></div>
<div class="metric"><div class="n">{min_score:.1f}</div><div>min score</div></div>
<div class="metric"><div class="n">{max_score:.1f}</div><div>max score</div></div>
</div>
<p class="muted">Agent: {esc(meta.get('agent'))}; model: {esc(meta.get('model') or 'default')}; max steps: {esc(meta.get('max_steps'))}; per-call timeout: {esc(meta.get('timeout_s'))}s; accumulated task duration: {duration:.1f}s.</p>
<details><summary>Smoke / clear logs</summary>
<h4>Smoke</h4><pre>{esc(smoke)}</pre>
<h4>Clear before</h4><pre>{esc(clear_before)}</pre>
<h4>Clear after</h4><pre>{esc(clear_after)}</pre>
</details>
</section>
<section>
<h2>Task Table</h2>
<table>
<thead><tr><th>#</th><th>Task</th><th>Family</th><th>Score</th><th>Pass</th><th>Submit</th><th>Turns</th><th>Seconds</th><th>Failure reasons</th></tr></thead>
<tbody>
{''.join(rows)}
</tbody>
</table>
</section>
{''.join(details)}
</main>
</body>
</html>
"""
    out = run_dir / "report.html"
    out.write_text(report, encoding="utf-8")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks-dir", default=str(ROOT / "tasks"))
    ap.add_argument("--task", action="append", help="Task directory name to run; repeatable.")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--agent", default="main")
    ap.add_argument("--model", default=None)
    ap.add_argument("--max-steps", type=int, default=14)
    ap.add_argument("--timeout", type=int, default=200)
    ap.add_argument("--run-dir", default=None)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--clear-before", action="store_true")
    ap.add_argument("--clear-after", action="store_true")
    args = ap.parse_args()

    tasks = discover_tasks(Path(args.tasks_dir), args.task)
    if args.limit is not None:
        tasks = tasks[:args.limit]
    if len(tasks) != 60 and not (args.task or args.limit):
        raise SystemExit(f"Expected 60 Red Dust tasks, found {len(tasks)}")

    run_dir = Path(args.run_dir) if args.run_dir else ROOT / "runs" / f"reddust_live_openclaw_{run_stamp()}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "tasks").mkdir(exist_ok=True)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")

    meta_path = run_dir / "run_meta.json"
    meta = read_json(meta_path, {}) or {}
    meta.update({
        "agent": args.agent,
        "model": args.model,
        "max_steps": args.max_steps,
        "timeout_s": args.timeout,
        "tasks_dir": str(Path(args.tasks_dir).resolve()),
        "run_dir": str(run_dir.resolve()),
        "updated_at": now_iso(),
    })
    meta.setdefault("created_at", now_iso())

    if args.smoke and not meta.get("smoke"):
        print("[setup] smoke: openclaw agent --agent main -m hello", flush=True)
        meta["smoke"] = run_smoke(args.agent, args.timeout, env)
        write_json(meta_path, meta)
    if args.clear_before and not meta.get("clear_before"):
        print("[setup] clear before batch", flush=True)
        meta["clear_before"] = run_clear(args.agent, args.timeout, env)
        write_json(meta_path, meta)

    write_json(meta_path, meta)
    total = len(tasks)
    completed = 0
    for index, task_dir in enumerate(tasks, start=1):
        detail_path = run_dir / "tasks" / f"{task_dir.name}.json"
        if detail_path.exists() and not args.force:
            existing = read_json(detail_path)
            print(
                f"[{index:02d}/{total:02d}] {task_dir.name} skip existing "
                f"score={existing.get('result', {}).get('score')}",
                flush=True,
            )
            completed += 1
            continue
        run_one_task(
            task_dir,
            index=index,
            total=total,
            args=args,
            run_dir=run_dir,
            env=env,
        )
        completed += 1
        meta["updated_at"] = now_iso()
        meta["completed_tasks"] = len(load_results(run_dir))
        write_json(meta_path, meta)
        report = render_report(run_dir, meta)
        print(f"[report] updated {report}", flush=True)

    if args.clear_after:
        print("[teardown] clear after batch", flush=True)
        meta["clear_after"] = run_clear(args.agent, args.timeout, env)
        write_json(meta_path, meta)

    meta["finished_at"] = now_iso()
    meta["completed_tasks"] = len(load_results(run_dir))
    write_json(meta_path, meta)
    report = render_report(run_dir, meta)
    print(f"[done] completed={completed}/{total} report={report}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
