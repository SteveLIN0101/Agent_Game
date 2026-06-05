#!/usr/bin/env python3
"""Run the live ``openclaw`` CLI agent through one Red Dust campaign.

Start the LAN server first, for example:

    PYTHONPATH=. python scripts/run_reddust_lan_server.py --port 7000

Then run:

    python scripts/run_reddust_campaign_agent.py --branch-policy auto --seed 20260603
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from openclaw.reddust.agent_bridge import extract_action  # noqa: E402


def request_json(method: str, url: str, payload: dict | None = None, token: str = "") -> dict:
    data = None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8")
        raise RuntimeError(f"{method} {url} failed: {exc.code} {body}") from exc


def call_openclaw_agent(
    *,
    agent: str,
    session_id: str,
    message: str,
    model: str,
    timeout: int,
) -> str:
    cmd = ["openclaw", "agent", "--agent", agent, "--json", "--session-id", session_id, "-m", message]
    if model:
        cmd += ["--model", model]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    out = proc.stdout.strip()
    brace = out.find("{")
    if brace == -1:
        return out
    try:
        data = json.loads(out[brace:])
    except json.JSONDecodeError:
        return out
    return "\n".join(item.get("text", "") for item in data.get("payloads", []))


def clear_agent_context(agent: str, model: str, timeout: int) -> None:
    cmd = ["openclaw", "agent", "--agent", agent, "-m", "/clear"]
    if model:
        cmd += ["--model", model]
    subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def observation_message(action_result: dict, used: int, max_steps: int) -> str:
    observation = action_result.get("observation")
    if observation is None:
        observation = action_result.get("error") or action_result
    return (
        f"OBSERVATION（campaign 当前任务，已用 {used}/{max_steps} 步）: "
        f"{json.dumps(observation, ensure_ascii=False, default=str)}\n"
        "输出下一个动作 JSON。若成功标准已满足，请调用 {\"tool\":\"submit\",\"args\":{}}。"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run openclaw agent through a Red Dust campaign API.")
    parser.add_argument("--base-url", default="http://127.0.0.1:7000")
    parser.add_argument("--auth-token", default="")
    parser.add_argument("--campaign-id", default="", help="Bind to an existing frontend-created campaign.")
    parser.add_argument("--seed", default=str(int(time.time())))
    parser.add_argument("--branch-policy", choices=["auto", "rescue", "lighthouse", "both"], default="auto")
    parser.add_argument("--task-selection", choices=["random", "first"], default="random")
    parser.add_argument("--agent", default="main")
    parser.add_argument("--model", default="")
    parser.add_argument("--max-steps-per-task", type=int, default=16)
    parser.add_argument("--timeout", type=int, default=200)
    parser.add_argument("--connect-agent", action="store_true", help="Call /campaigns/{id}/connect before playing.")
    parser.add_argument("--wait-for-start", action="store_true", help="Poll until the frontend calls /start.")
    parser.add_argument("--clear-before", action="store_true")
    parser.add_argument("--clear-after", action="store_true")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    if args.clear_before:
        clear_agent_context(args.agent, args.model, args.timeout)

    if args.campaign_id:
        campaign_id = args.campaign_id
        request_json("GET", f"{base}/campaigns/{campaign_id}/state", token=args.auth_token)
    else:
        created = request_json("POST", f"{base}/campaigns", {
            "seed": args.seed,
            "branch_policy": args.branch_policy,
            "task_selection": args.task_selection,
            "agent_id": args.agent,
            "model_id": args.model,
            "max_steps_per_task": args.max_steps_per_task,
        }, args.auth_token)
        campaign_id = created["campaign_id"]
    if args.connect_agent or args.campaign_id:
        request_json("POST", f"{base}/campaigns/{campaign_id}/connect", {
            "agent_id": args.agent,
            "model_id": args.model,
            "client": "openclaw-cli-runner",
        }, args.auth_token)
    if args.wait_for_start:
        print(f"Waiting for frontend start on campaign={campaign_id}...")
        while True:
            state = request_json("GET", f"{base}/campaigns/{campaign_id}/state", token=args.auth_token)
            if state.get("status") != "waiting_for_start":
                break
            time.sleep(1.0)
    session_id = f"reddust-campaign-{campaign_id}-{int(time.time())}"
    print(f"▶ campaign={campaign_id} seed={args.seed} policy={args.branch_policy}")

    task_counter = 0
    while True:
        state = request_json("GET", f"{base}/campaigns/{campaign_id}/state", token=args.auth_token)
        if state["status"] == "complete":
            break
        current = state["current_run"]
        task_counter += 1
        print(
            f"\n[{task_counter:02d}] Day {state['global_state']['day']} "
            f"{state['active_branch']} {current['slot_id']} -> {current['task_id']} {current['title']}"
        )
        brief = request_json("GET", f"{base}/campaigns/{campaign_id}/brief", token=args.auth_token)
        message = brief["brief"]
        submitted = False

        for step in range(1, args.max_steps_per_task + 1):
            reply = call_openclaw_agent(
                agent=args.agent,
                session_id=session_id,
                message=message,
                model=args.model,
                timeout=args.timeout,
            )
            action = extract_action(reply)
            if action is None:
                print(f"  step {step:02d}: invalid JSON")
                message = '上一条不是合法 JSON。只输出一个 JSON 对象：{"tool":"...","args":{}}。'
                continue
            print(f"  step {step:02d}: {action.get('tool')}")
            action_result = request_json(
                "POST",
                f"{base}/campaigns/{campaign_id}/actions",
                action,
                args.auth_token,
            )
            if action.get("tool") == "submit" or action_result.get("done"):
                submitted = True
                score = action_result.get("submitted_result", {}).get("score")
                print(f"  submitted score={score}")
                break
            message = observation_message(action_result, step, args.max_steps_per_task)

        if not submitted:
            forced = request_json("POST", f"{base}/campaigns/{campaign_id}/submit", {}, args.auth_token)
            score = forced.get("submitted_result", {}).get("score")
            print(f"  max steps reached; forced submit score={score}")

    final_state = request_json("GET", f"{base}/campaigns/{campaign_id}/state", token=args.auth_token)
    print("\n" + "=" * 72)
    print(f"Campaign complete: {campaign_id}")
    print(f"Ending: {final_state.get('ending', {}).get('title')}")
    print(f"Report: {base}/campaigns/{campaign_id}/report.html")
    print(f"Trace:  {base}/campaigns/{campaign_id}/trace")
    print("=" * 72)

    if args.clear_after:
        clear_agent_context(args.agent, args.model, args.timeout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
