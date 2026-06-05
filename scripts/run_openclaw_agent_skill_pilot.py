"""Run the OpenClaw agent-skill pilot through the OpenClaw CLI gateway.

This harness intentionally uses the real `openclaw agent` one-shot CLI for
each condition. The only condition difference is whether the prompt includes
`openclaw_game.skill.md`.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXPERIMENT = PROJECT_ROOT / "experiments" / "agent_skill_pilot.yaml"
DEFAULT_CONFIG = (
    PROJECT_ROOT
    / "workspaces"
    / "openclaw-gateway"
    / ".openclaw-state"
    / "agent-skill-bench"
    / "openclaw.json"
)
DEFAULT_OUT_DIR = PROJECT_ROOT / "workspaces" / "agent-skill-utility-pilot" / "live_agent_outputs"
DEFAULT_AGENT_SCRIPT = (
    Path("/Users/steve/Documents/卓正/卓正正式/OpenClaw_Mutl_openclaw_dominant")
    / "scripts"
    / "openclaw_agent_once.sh"
)


def load_experiment(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_gateway(path: Path) -> tuple[str, str]:
    config = json.loads(path.read_text(encoding="utf-8"))
    port = config["gateway"]["port"]
    token = config["gateway"]["auth"]["token"]
    return f"ws://127.0.0.1:{port}", token


def slug(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_.-]+", "-", value)
    return cleaned.strip("-")[:180]


def make_prompt(
    task_id: str,
    condition: str,
    pilot_run_id: str,
    agent_id: str,
    model_id: str,
    trial_index: int,
    seed: str,
    skill_text: str,
) -> str:
    condition_header = (
        "CONDITION: control/no-skill. Do not use openclaw_game.skill.md; use only the task instructions returned by the OpenClaw benchmark tools."
        if condition == "control"
        else (
            "CONDITION: skill. The following is openclaw_game.skill.md; follow it as your task workflow guide.\n\n"
            "----- BEGIN openclaw_game.skill.md -----\n"
            f"{skill_text}\n"
            "----- END openclaw_game.skill.md -----"
        )
    )
    return f"""You are running one OpenClaw benchmark task through the official benchmark MCP tools.

{condition_header}

Tool policy:
- Use ONLY tools whose names start with `openclaw__openclaw__`.
- Do not use host `read`, `edit`, `write`, `exec`, `process`, browser, web, memory, or file tools.
- Never inspect local repository task files, hidden tests, expected files, or verifier files outside the OpenClaw benchmark tools.
- For `openclaw__openclaw__run_shell`, do not put `cd`, `&&`, or shell chaining in `command`; use the `workdir` argument when needed.
- If a benchmark tool returns an error, adapt once when obvious; otherwise submit or report the failure rather than using host tools.

Start by calling `openclaw__openclaw__get_task` with exactly:
- task_id: `{task_id}`
- pilot_run_id: `{pilot_run_id}`
- agent_id: `{agent_id}`
- model_id: `{model_id}`
- skill_variant: `{condition}`
- trial_index: {trial_index}
- seed: `{seed}`

Then complete the task using the benchmark workspace, run useful visible tests, call `openclaw__openclaw__submit`, and finally reply with only compact JSON:
{{"task_id":"{task_id}","condition":"{condition}","total_score":<number-or-null>,"verifier_passed":<true-or-false-or-null>,"submitted":<true-or-false>}}"""


def run_one(
    *,
    script: Path,
    gateway_url: str,
    token: str,
    session_id: str,
    message: str,
    out_file: Path,
    timeout: int,
) -> dict[str, Any]:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(script),
        "--url",
        gateway_url,
        "--token",
        token,
        "--session",
        session_id,
        "--message",
        message,
        "--json",
        "--out",
        str(out_file),
    ]
    started = time.time()
    proc = subprocess.run(
        cmd,
        cwd=str(PROJECT_ROOT),
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    elapsed = time.time() - started
    return {
        "session_id": session_id,
        "out_file": str(out_file),
        "returncode": proc.returncode,
        "elapsed_seconds": round(elapsed, 3),
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", type=Path, default=DEFAULT_EXPERIMENT)
    parser.add_argument("--gateway-config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--agent-script", type=Path, default=DEFAULT_AGENT_SCRIPT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--pilot-run-id", default="live-openclaw-agent-pilot-20260528")
    parser.add_argument("--agent-id", default="openclaw-agent-cli")
    parser.add_argument("--model-id", default="deepseek-v4-flash")
    parser.add_argument("--seed", default="")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--only-task", action="append", default=[])
    parser.add_argument("--only-condition", choices=["control", "skill"], default="")
    parser.add_argument(
        "--session-suffix",
        default="",
        help="Append a suffix to session/output names for targeted reruns.",
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()

    experiment = load_experiment(args.experiment)
    seed = args.seed or str(experiment.get("seed", ""))
    gateway_url, token = load_gateway(args.gateway_config)
    skill_text = (PROJECT_ROOT / "openclaw_game.skill.md").read_text(encoding="utf-8")
    run_log_path = args.out_dir / f"{args.pilot_run_id}.runs.jsonl"

    planned: list[tuple[str, str]] = []
    only_tasks = set(args.only_task)
    for task in experiment["main_tasks"]:
        task_id = task["task_id"]
        if only_tasks and task_id not in only_tasks:
            continue
        for condition in task.get("order", ["control", "skill"]):
            if args.only_condition and condition != args.only_condition:
                continue
            planned.append((task_id, condition))
    if args.limit:
        planned = planned[: args.limit]

    print(f"pilot_run_id={args.pilot_run_id}")
    print(f"gateway_url={gateway_url}")
    print(f"planned_runs={len(planned)}")
    session_suffix = slug(args.session_suffix)

    for index, (task_id, condition) in enumerate(planned, 1):
        suffix = f"-{session_suffix}" if session_suffix else ""
        file_suffix = f"__{session_suffix}" if session_suffix else ""
        session_id = slug(f"{args.pilot_run_id}-{task_id}-{condition}-t0{suffix}")
        out_file = args.out_dir / args.pilot_run_id / f"{slug(task_id)}__{condition}{file_suffix}.json"
        if args.resume and out_file.exists():
            print(f"[{index}/{len(planned)}] skip existing {task_id} {condition}")
            continue

        message = make_prompt(
            task_id=task_id,
            condition=condition,
            pilot_run_id=args.pilot_run_id,
            agent_id=args.agent_id,
            model_id=args.model_id,
            trial_index=0,
            seed=seed,
            skill_text=skill_text,
        )
        print(f"[{index}/{len(planned)}] run {task_id} {condition}")
        result = run_one(
            script=args.agent_script,
            gateway_url=gateway_url,
            token=token,
            session_id=session_id,
            message=message,
            out_file=out_file,
            timeout=args.timeout,
        )
        result.update({
            "task_id": task_id,
            "condition": condition,
            "pilot_run_id": args.pilot_run_id,
            "session_suffix": session_suffix,
        })
        with open(run_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
        status = "ok" if result["returncode"] == 0 else f"exit={result['returncode']}"
        print(f"[{index}/{len(planned)}] done {task_id} {condition} {status} {result['elapsed_seconds']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
