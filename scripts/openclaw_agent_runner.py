#!/usr/bin/env python3
"""Have the live ``openclaw`` agent solve a Red Dust task, then auto-score it.

    python scripts/openclaw_agent_runner.py <task_dir> [--agent main] [--model id]
                                            [--max-steps N] [--timeout SECS]

Each turn calls:  openclaw agent --agent <id> --json --session-id <fresh> -m <msg>
The agent replies with a JSON action; the bridge executes it against the task's
tools and feeds back the observation; on ``submit`` the World is graded.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from openclaw.reddust.agent_bridge import run_agent  # noqa: E402


def make_call_agent(agent_id, session_id, model, timeout, log):
    def call_agent(message: str) -> str:
        cmd = ["openclaw", "agent", "--agent", agent_id, "--json",
               "--session-id", session_id, "-m", message]
        if model:
            cmd += ["--model", model]
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            log(f"  ! agent call timed out after {timeout}s")
            return ""
        out = p.stdout.strip()
        brace = out.find("{")
        if brace == -1:
            log(f"  ! no JSON from CLI (stderr tail: {p.stderr.strip()[-160:]})")
            return ""
        try:
            data = json.loads(out[brace:])
        except json.JSONDecodeError:
            return out
        return "\n".join(pl.get("text", "") for pl in data.get("payloads", []))
    return call_agent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("task_dir")
    ap.add_argument("--agent", default="main")
    ap.add_argument("--model", default=None)
    ap.add_argument("--max-steps", type=int, default=14)
    ap.add_argument("--timeout", type=int, default=200)
    args = ap.parse_args()

    task_dir = Path(args.task_dir)
    session_id = f"reddust-{task_dir.name}-{int(time.time())}-{os.getpid()}"
    print(f"▶ openclaw agent='{args.agent}' session='{session_id}'  task={task_dir.name}")
    print(f"  (每轮约 10–15s，最多 {args.max_steps} 步)\n")

    step = {"n": 0}

    def log(msg):
        print(msg, flush=True)

    base_call = make_call_agent(args.agent, session_id, args.model, args.timeout, log)

    def traced_call(message):
        step["n"] += 1
        t0 = time.time()
        reply = base_call(message)
        dt = time.time() - t0
        snippet = reply.replace("\n", " ")[:90]
        log(f"  step {step['n']:>2} ({dt:4.1f}s) agent → {snippet}")
        return reply

    r = run_agent(task_dir, traced_call, max_steps=args.max_steps)

    print("\n" + "═" * 64)
    print(f"  {r['task_id']}   submitted={r['submitted']}")
    print(f"  得分 SCORE: {r['score']}/100  (可见 {r['visible_score']} · 隐藏 {r['hidden_score']})  "
          f"{'✅ PASS' if r['passed_all'] else '❌'}")
    for c in r["checks"]:
        tag = "".join(t for t in [" [critical]" if c["critical"] else "",
                                  " [hidden]" if c["hidden"] else ""])
        print(f"    {'✓' if c['passed'] else '✗'} {c['desc']}{tag}")
    if r["failure_reasons"]:
        print("  失败原因:")
        for fr in r["failure_reasons"]:
            print(f"      ✗ {fr}")
    beats = " → ".join(e["beat"] for e in r["trajectory"] if e.get("beat"))
    print(f"  实际轨迹: {beats}")
    print("═" * 64)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
