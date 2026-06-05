#!/usr/bin/env python3
"""Evaluate paired OpenClaw agent output directories.

This is a one-command evaluator for already-produced solver artifacts. It
copies each condition's task directory to a temporary evaluator workspace,
injects evaluator-only expected/verifier files, runs every task verifier, and
writes paired control-vs-skill JSONL plus a compact Markdown report.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

import yaml


RESULT_RE = re.compile(r"RESULT:\s+(PASS|FAIL)\s+—\s+(\S+)(.*)")
LEAF_RE = re.compile(r"json leaf score:\s+(\d+)/(\d+)")


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_timings(root: Path) -> dict[str, dict[str, Any]]:
    timing_path = root.parent / "test_timing.jsonl"
    timings: dict[str, dict[str, Any]] = {}
    if not timing_path.exists():
        return timings
    for line in timing_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        task_id = row.get("task_id")
        if task_id:
            timings[task_id] = row
    return timings


def copy_evaluator_materials(evaluator_task: Path, task_copy: Path) -> None:
    for item in ("expected", "verifier", "source_manifest.json"):
        src = evaluator_task / item
        if not src.exists():
            continue
        dst = task_copy / item
        if dst.exists():
            shutil.rmtree(dst) if dst.is_dir() else dst.unlink()
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)


def parse_verifier_output(stdout: str, exit_code: int) -> dict[str, Any]:
    match = RESULT_RE.search(stdout)
    leaf_match = LEAF_RE.search(stdout)
    leaf_score = None
    leaf_total = None
    leaf_ratio = None
    if leaf_match:
        leaf_score = int(leaf_match.group(1))
        leaf_total = int(leaf_match.group(2))
        leaf_ratio = leaf_score / leaf_total if leaf_total else None
    return {
        "passed": exit_code == 0,
        "result_status": match.group(1) if match else "",
        "result_task_id": match.group(2) if match else "",
        "result_tail": match.group(3).strip() if match else "",
        "leaf_score": leaf_score,
        "leaf_total": leaf_total,
        "leaf_ratio": leaf_ratio,
    }


def classify_failure(stdout: str, stderr: str, exit_code: int) -> list[str]:
    if exit_code == 0:
        return []
    text = f"{stdout}\n{stderr}".lower()
    tags = []
    if "missing output" in text:
        tags.append("F4_output_contract")
    if "json parse error" in text:
        tags.append("F4_output_contract")
    if "mismatch" in text or "expected" in text:
        tags.append("F8_domain_error")
    if "traceback" in text or "no such file" in text:
        tags.append("F9_infra_or_verifier_error")
    return tags or ["F8_domain_error"]


def run_verifier(task_dir: Path, python_bin: str) -> dict[str, Any]:
    started = time.perf_counter()
    proc = subprocess.run(
        [python_bin, "verifier/verify.py"],
        cwd=task_dir,
        capture_output=True,
        text=True,
    )
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    parsed = parse_verifier_output(proc.stdout, proc.returncode)
    return {
        **parsed,
        "exit_code": proc.returncode,
        "stdout_tail": proc.stdout[-2000:],
        "stderr_tail": proc.stderr[-2000:],
        "verifier_elapsed_ms": elapsed_ms,
        "failure_tags": classify_failure(proc.stdout, proc.stderr, proc.returncode),
    }


def score_from_verifier(result: dict[str, Any]) -> float:
    if result["passed"]:
        return 100.0
    if result["leaf_ratio"] is not None:
        return round(result["leaf_ratio"] * 100, 2)
    return 0.0


def evaluate_condition(
    *,
    condition: str,
    submissions_root: Path,
    evaluator_root: Path,
    work_root: Path,
    python_bin: str,
    pilot_run_id: str,
    agent_id: str,
    model_id: str,
    limit: int | None,
) -> list[dict[str, Any]]:
    timings = load_timings(submissions_root)
    task_ids = sorted(p.name for p in evaluator_root.iterdir() if p.is_dir())
    if limit:
        task_ids = task_ids[:limit]

    records = []
    for task_id in task_ids:
        evaluator_task = evaluator_root / task_id
        submission_task = submissions_root / task_id
        task_meta = load_yaml(evaluator_task / "task.yaml")
        task_copy = work_root / condition / task_id
        if task_copy.exists():
            shutil.rmtree(task_copy)
        if submission_task.exists():
            shutil.copytree(submission_task, task_copy)
        else:
            shutil.copytree(evaluator_task, task_copy)
            outputs = task_copy / "outputs"
            if outputs.exists():
                shutil.rmtree(outputs)
            outputs.mkdir(parents=True, exist_ok=True)
        copy_evaluator_materials(evaluator_task, task_copy)

        verifier = run_verifier(task_copy, python_bin)
        timing = timings.get(task_id, {})
        record = {
            "task_id": task_id,
            "role": task_meta.get("role", ""),
            "difficulty": task_meta.get("difficulty", ""),
            "source_benchmark": task_meta.get("source_benchmark", ""),
            "condition": condition,
            "pass": verifier["passed"],
            "score": {
                "total_score": score_from_verifier(verifier),
                "verifier_passed": verifier["passed"],
            },
            "components": {
                "leaf_score": verifier["leaf_score"],
                "leaf_total": verifier["leaf_total"],
                "leaf_ratio": verifier["leaf_ratio"],
            },
            "elapsed_seconds": (
                timing.get("elapsed_ms") / 1000
                if isinstance(timing.get("elapsed_ms"), (int, float))
                else None
            ),
            "verifier_elapsed_ms": verifier["verifier_elapsed_ms"],
            "failure_tags": verifier["failure_tags"],
            "pilot_metadata": {
                "pilot_run_id": pilot_run_id,
                "agent_id": agent_id,
                "model_id": model_id,
                "skill_variant": condition,
                "trial_index": 0,
                "seed": "",
            },
            "verifier": {
                "exit_code": verifier["exit_code"],
                "stdout_tail": verifier["stdout_tail"],
                "stderr_tail": verifier["stderr_tail"],
            },
        }
        records.append(record)
    return records


def pair_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for record in records:
        grouped[record["task_id"]][record["condition"]] = record

    pairs = []
    for task_id, by_condition in sorted(grouped.items()):
        if "control" not in by_condition or "skill" not in by_condition:
            continue
        control = by_condition["control"]
        skill = by_condition["skill"]
        pairs.append({
            "task_id": task_id,
            "role": control.get("role") or skill.get("role", ""),
            "difficulty": control.get("difficulty") or skill.get("difficulty", ""),
            "source_benchmark": control.get("source_benchmark")
            or skill.get("source_benchmark", ""),
            "control": control,
            "skill": skill,
            "score_delta": skill["score"]["total_score"]
            - control["score"]["total_score"],
            "pass_delta": int(skill["pass"]) - int(control["pass"]),
        })
    return pairs


def classify_pair(pair: dict[str, Any], threshold: float = 5.0) -> str:
    control_pass = pair["control"]["pass"]
    skill_pass = pair["skill"]["pass"]
    if skill_pass and not control_pass:
        return "win"
    if control_pass and not skill_pass:
        return "loss"
    if pair["score_delta"] >= threshold:
        return "win"
    if pair["score_delta"] <= -threshold:
        return "loss"
    return "tie"


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    pairs = pair_records(records)
    labels = [classify_pair(pair) for pair in pairs]
    counts = Counter(labels)
    by_role = defaultdict(list)
    for pair in pairs:
        by_role[pair["role"]].append(pair)
    return {
        "n_pairs": len(pairs),
        "control_pass_rate": mean(
            int(pair["control"]["pass"]) for pair in pairs
        ) if pairs else 0.0,
        "skill_pass_rate": mean(
            int(pair["skill"]["pass"]) for pair in pairs
        ) if pairs else 0.0,
        "delta_pass_at_1": mean(pair["pass_delta"] for pair in pairs)
        if pairs else 0.0,
        "delta_score": mean(pair["score_delta"] for pair in pairs)
        if pairs else 0.0,
        "wins": counts["win"],
        "ties": counts["tie"],
        "losses": counts["loss"],
        "net_win_rate": (counts["win"] - counts["loss"]) / len(pairs)
        if pairs else 0.0,
        "by_role": {
            role: {
                "n": len(items),
                "control_pass_rate": mean(int(p["control"]["pass"]) for p in items),
                "skill_pass_rate": mean(int(p["skill"]["pass"]) for p in items),
                "wins": Counter(classify_pair(p) for p in items)["win"],
                "ties": Counter(classify_pair(p) for p in items)["tie"],
                "losses": Counter(classify_pair(p) for p in items)["loss"],
                "delta_score": mean(p["score_delta"] for p in items),
            }
            for role, items in sorted(by_role.items())
        },
        "pairs": pairs,
    }


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def render_report(summary: dict[str, Any]) -> str:
    lines = [
        "# OpenClaw Agent Output Skill/No-Skill Evaluation",
        "",
        "This report evaluates paired existing agent output directories by running each task verifier in a temporary evaluator workspace.",
        "",
        "## Overall",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| pairs | {summary['n_pairs']} |",
        f"| control pass rate | {fmt(summary['control_pass_rate'])} |",
        f"| skill pass rate | {fmt(summary['skill_pass_rate'])} |",
        f"| delta pass@1 | {fmt(summary['delta_pass_at_1'])} |",
        f"| delta score | {fmt(summary['delta_score'])} |",
        f"| wins / ties / losses | {summary['wins']} / {summary['ties']} / {summary['losses']} |",
        f"| net win rate | {fmt(summary['net_win_rate'])} |",
        "",
        "## By Role",
        "",
        "| role | n | control pass | skill pass | W/T/L | delta score |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for role, row in summary["by_role"].items():
        lines.append(
            f"| {role} | {row['n']} | {fmt(row['control_pass_rate'])} | "
            f"{fmt(row['skill_pass_rate'])} | "
            f"{row['wins']}/{row['ties']}/{row['losses']} | "
            f"{fmt(row['delta_score'])} |"
        )

    lines += [
        "",
        "## Task Pairs",
        "",
        "| task | role | control | skill | delta | label |",
        "|---|---|---:|---:|---:|---|",
    ]
    for pair in summary["pairs"]:
        lines.append(
            f"| {pair['task_id']} | {pair['role']} | "
            f"{int(pair['control']['pass'])} / {fmt(pair['control']['score']['total_score'])} | "
            f"{int(pair['skill']['pass'])} / {fmt(pair['skill']['score']['total_score'])} | "
            f"{fmt(pair['score_delta'])} | {classify_pair(pair)} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--evaluator-root",
        type=Path,
        default=Path("openclaw_core6_team_sync/openclaw_core6_tasks/tasks"),
    )
    parser.add_argument(
        "--control-root",
        type=Path,
        required=True,
        help="Task root for no-skill/control agent outputs",
    )
    parser.add_argument(
        "--skill-root",
        type=Path,
        required=True,
        help="Task root for skill/treatment agent outputs",
    )
    parser.add_argument("--pilot-run-id", default="agent-output-paired-eval")
    parser.add_argument("--agent-id", default="agent")
    parser.add_argument("--model-id", default="")
    parser.add_argument(
        "--out-jsonl",
        type=Path,
        default=Path("runs/agent_skill_output_eval.jsonl"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("workspaces/agent-skill-utility-pilot/agent_skill_output_eval.md"),
    )
    parser.add_argument("--python-bin", default=sys.executable)
    parser.add_argument("--workdir", type=Path)
    parser.add_argument("--keep-workdir", action="store_true")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    evaluator_root = args.evaluator_root.resolve()
    control_root = args.control_root.resolve()
    skill_root = args.skill_root.resolve()
    work_root = args.workdir
    temp_dir = None
    if work_root is None:
        temp_dir = tempfile.TemporaryDirectory(prefix="openclaw-agent-eval-")
        work_root = Path(temp_dir.name)
    else:
        work_root.mkdir(parents=True, exist_ok=True)

    try:
        records = []
        for condition, root in (("control", control_root), ("skill", skill_root)):
            records.extend(
                evaluate_condition(
                    condition=condition,
                    submissions_root=root,
                    evaluator_root=evaluator_root,
                    work_root=work_root,
                    python_bin=args.python_bin,
                    pilot_run_id=args.pilot_run_id,
                    agent_id=args.agent_id,
                    model_id=args.model_id,
                    limit=args.limit,
                )
            )
        args.out_jsonl.parent.mkdir(parents=True, exist_ok=True)
        with args.out_jsonl.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")

        summary = summarize(records)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(render_report(summary), encoding="utf-8")
        print(json.dumps({
            "records": len(records),
            "pairs": summary["n_pairs"],
            "control_pass_rate": summary["control_pass_rate"],
            "skill_pass_rate": summary["skill_pass_rate"],
            "delta_pass_at_1": summary["delta_pass_at_1"],
            "delta_score": summary["delta_score"],
            "wins": summary["wins"],
            "ties": summary["ties"],
            "losses": summary["losses"],
            "jsonl": str(args.out_jsonl),
            "report": str(args.report),
            "workdir": str(work_root) if args.keep_workdir else "",
        }, indent=2, ensure_ascii=False))
    finally:
        if temp_dir is not None and not args.keep_workdir:
            temp_dir.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
