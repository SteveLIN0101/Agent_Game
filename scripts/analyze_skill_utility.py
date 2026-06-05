"""Analyze OpenClaw paired skill-utility pilot results.

Reads JSONL records written by openclaw__submit() and reports paired
control-vs-skill deltas without changing verifier scores.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


CONTROL = "control"
SKILL = "skill"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        raise FileNotFoundError(path)
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSONL") from exc
    return records


def load_task_metadata(path: Path | None) -> dict[str, dict[str, str]]:
    if not path or not path.exists():
        return {}
    try:
        import yaml
    except ImportError:
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    metadata: dict[str, dict[str, str]] = {}
    for task in data.get("main_tasks", []):
        task_id = task.get("task_id")
        if not task_id:
            continue
        metadata[task_id] = {
            "role": task.get("role", ""),
            "difficulty": task.get("difficulty", ""),
        }
    return metadata


def condition(record: dict[str, Any]) -> str:
    value = record.get("condition") or record.get("skill_variant")
    if value:
        return str(value)
    return str(record.get("pilot_metadata", {}).get("skill_variant", CONTROL))


def trial_index(record: dict[str, Any]) -> int:
    value = record.get("trial_index")
    if value is None:
        value = record.get("pilot_metadata", {}).get("trial_index", 0)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def total_score(record: dict[str, Any]) -> float:
    score = record.get("score", {})
    if isinstance(score, dict):
        return float(score.get("total_score", 0.0))
    return float(record.get("total_score", 0.0))


def passed(record: dict[str, Any]) -> bool:
    if "pass" in record:
        return bool(record["pass"])
    score = record.get("score", {})
    if isinstance(score, dict):
        return bool(score.get("verifier_passed", False))
    return bool(record.get("verifier_passed", False))


def cost_value(record: dict[str, Any]) -> float | None:
    for key in ("total_cost_usd", "cost_usd", "model_cost_usd"):
        if record.get(key) not in (None, ""):
            return max(float(record[key]), 0.01)
    elapsed = record.get("elapsed_seconds")
    if elapsed not in (None, ""):
        return max(float(elapsed), 0.001)
    return None


def pair_group_key(record: dict[str, Any]) -> tuple[str, str, str, str]:
    meta = record.get("pilot_metadata", {})
    return (
        str(meta.get("pilot_run_id", "")),
        str(meta.get("agent_id", "")),
        str(meta.get("model_id", "")),
        str(record.get("task_id", "")),
    )


def filter_records(
    records: list[dict[str, Any]],
    *,
    pilot_run_id: str = "",
) -> list[dict[str, Any]]:
    if not pilot_run_id:
        return records
    return [
        record
        for record in records
        if str(record.get("pilot_metadata", {}).get("pilot_run_id", "")) == pilot_run_id
    ]


def build_main_pairs(
    records: list[dict[str, Any]],
    task_metadata: dict[str, dict[str, str]] | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    grouped: dict[tuple[str, str, str, str], dict[str, list[dict[str, Any]]]] = (
        defaultdict(lambda: defaultdict(list))
    )
    for record in records:
        grouped[pair_group_key(record)][condition(record)].append(record)

    pairs: list[dict[str, Any]] = []
    incomplete: list[str] = []
    task_metadata = task_metadata or {}
    for key, by_condition in grouped.items():
        if CONTROL not in by_condition or SKILL not in by_condition:
            incomplete.append(key[-1])
            continue
        control = sorted(by_condition[CONTROL], key=trial_index)[0]
        skill = sorted(by_condition[SKILL], key=trial_index)[0]
        task_id = key[-1]
        meta = task_metadata.get(task_id, {})
        role = meta.get("role") or control.get("role") or skill.get("role", "")
        difficulty = meta.get("difficulty") or control.get("difficulty", "")
        pairs.append({
            "task_id": task_id,
            "role": role,
            "difficulty": difficulty,
            "control": control,
            "skill": skill,
            "score_delta": total_score(skill) - total_score(control),
            "pass_delta": int(passed(skill)) - int(passed(control)),
            "control_pass": passed(control),
            "skill_pass": passed(skill),
        })
    return pairs, incomplete


def classify_pair(pair: dict[str, Any], threshold: float = 5.0) -> str:
    if pair["skill_pass"] and not pair["control_pass"]:
        return "win"
    if pair["control_pass"] and not pair["skill_pass"]:
        return "loss"
    if pair["score_delta"] >= threshold:
        return "win"
    if pair["score_delta"] <= -threshold:
        return "loss"
    return "tie"


def exact_sign_test(wins: int, losses: int) -> float | None:
    n = wins + losses
    if n == 0:
        return None
    tail = min(wins, losses)
    probability = sum(math.comb(n, i) for i in range(tail + 1)) / (2 ** n)
    return min(1.0, 2.0 * probability)


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = (len(ordered) - 1) * q
    lo = math.floor(idx)
    hi = math.ceil(idx)
    if lo == hi:
        return ordered[int(idx)]
    return ordered[lo] * (hi - idx) + ordered[hi] * (idx - lo)


def bootstrap_ci(
    pairs: list[dict[str, Any]],
    metric_name: str,
    iterations: int = 10_000,
    seed: int = 20260527,
) -> tuple[float, float]:
    if not pairs:
        return (0.0, 0.0)
    rng = random.Random(seed)
    strata: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for pair in pairs:
        strata[(pair.get("role", ""), pair.get("difficulty", ""))].append(pair)

    def metric(sample: list[dict[str, Any]]) -> float:
        if metric_name == "pass_delta":
            return mean(p["pass_delta"] for p in sample)
        if metric_name == "score_delta":
            return mean(p["score_delta"] for p in sample)
        if metric_name == "net_win_rate":
            labels = [classify_pair(p) for p in sample]
            return (labels.count("win") - labels.count("loss")) / len(sample)
        if metric_name == "cost_ratio":
            ratios = []
            for p in sample:
                c = cost_value(p["control"])
                s = cost_value(p["skill"])
                if c and s:
                    ratios.append(s / c)
            return mean(ratios) if ratios else 0.0
        raise ValueError(metric_name)

    values = []
    stratum_values = list(strata.values())
    for _ in range(iterations):
        sample = []
        for stratum in stratum_values:
            sample.extend(rng.choice(stratum) for _ in range(len(stratum)))
        values.append(metric(sample))
    return (percentile(values, 0.025), percentile(values, 0.975))


def summarize_pairs(pairs: list[dict[str, Any]], bootstrap_n: int) -> dict[str, Any]:
    labels = [classify_pair(pair) for pair in pairs]
    counts = Counter(labels)
    wins = counts["win"]
    losses = counts["loss"]
    non_tie = wins + losses
    cost_ratios = []
    for pair in pairs:
        c = cost_value(pair["control"])
        s = cost_value(pair["skill"])
        if c and s:
            cost_ratios.append(s / c)
    return {
        "n_pairs": len(pairs),
        "delta_pass_at_1": mean([p["pass_delta"] for p in pairs]) if pairs else 0.0,
        "delta_score": mean([p["score_delta"] for p in pairs]) if pairs else 0.0,
        "wins": wins,
        "ties": counts["tie"],
        "losses": losses,
        "net_win_rate": (wins - losses) / len(pairs) if pairs else 0.0,
        "conditional_win_rate": wins / non_tie if non_tie else 0.0,
        "sign_test_p": exact_sign_test(wins, losses),
        "mean_cost_ratio": mean(cost_ratios) if cost_ratios else 0.0,
        "ci": {
            "delta_pass_at_1": bootstrap_ci(pairs, "pass_delta", bootstrap_n),
            "delta_score": bootstrap_ci(pairs, "score_delta", bootstrap_n),
            "net_win_rate": bootstrap_ci(pairs, "net_win_rate", bootstrap_n),
            "cost_ratio": bootstrap_ci(pairs, "cost_ratio", bootstrap_n),
        },
    }


def summarize_reliability(records: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[tuple[str, str, str, str], dict[str, list[dict[str, Any]]]] = (
        defaultdict(lambda: defaultdict(list))
    )
    for record in records:
        grouped[pair_group_key(record)][condition(record)].append(record)

    rows = []
    for key, by_condition in grouped.items():
        if CONTROL not in by_condition or SKILL not in by_condition:
            continue
        control = by_condition[CONTROL]
        skill = by_condition[SKILL]
        if len(control) < 2 or len(skill) < 2:
            continue
        k = min(len(control), len(skill))
        c_pass = sum(passed(r) for r in control[:k])
        s_pass = sum(passed(r) for r in skill[:k])
        rows.append({
            "task_id": key[-1],
            "k": k,
            "control_pass_at_k": int(c_pass >= 1),
            "skill_pass_at_k": int(s_pass >= 1),
            "control_pass_k_rate": c_pass / k,
            "skill_pass_k_rate": s_pass / k,
            "control_all_pass_k": int(c_pass == k),
            "skill_all_pass_k": int(s_pass == k),
        })

    if not rows:
        return {"n_tasks": 0, "rows": []}
    return {
        "n_tasks": len(rows),
        "delta_pass_at_k": mean(
            r["skill_pass_at_k"] - r["control_pass_at_k"] for r in rows
        ),
        "delta_pass_k_rate": mean(
            r["skill_pass_k_rate"] - r["control_pass_k_rate"] for r in rows
        ),
        "delta_all_pass_k": mean(
            r["skill_all_pass_k"] - r["control_all_pass_k"] for r in rows
        ),
        "rows": rows,
    }


def summarize_failures(records: list[dict[str, Any]]) -> dict[str, Counter]:
    counters = {CONTROL: Counter(), SKILL: Counter()}
    for record in records:
        cond = condition(record)
        if cond not in counters:
            continue
        tags = record.get("failure_tags") or record.get(
            "trace_summary", {}
        ).get("failure_tags", [])
        counters[cond].update(tags)
    return counters


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    if isinstance(value, tuple):
        return f"[{value[0]:.3f}, {value[1]:.3f}]"
    return str(value)


def render_markdown(
    pair_summary: dict[str, Any],
    pairs: list[dict[str, Any]],
    reliability: dict[str, Any],
    failures: dict[str, Counter],
    incomplete: list[str],
) -> str:
    lines = ["# OpenClaw Agent-Skill Utility Pilot Report", ""]
    lines += [
        "## Main Paired Results",
        "",
        "| metric | value | 95% CI |",
        "|---|---:|---:|",
        f"| pairs | {pair_summary['n_pairs']} | |",
        f"| delta pass@1 | {fmt(pair_summary['delta_pass_at_1'])} | {fmt(pair_summary['ci']['delta_pass_at_1'])} |",
        f"| delta total_score | {fmt(pair_summary['delta_score'])} | {fmt(pair_summary['ci']['delta_score'])} |",
        f"| net win rate | {fmt(pair_summary['net_win_rate'])} | {fmt(pair_summary['ci']['net_win_rate'])} |",
        f"| mean cost ratio | {fmt(pair_summary['mean_cost_ratio'])} | {fmt(pair_summary['ci']['cost_ratio'])} |",
        f"| sign-test p | {fmt(pair_summary['sign_test_p'])} | |",
        "",
        "## Win/Tie/Loss",
        "",
        "| wins | ties | losses | conditional win rate |",
        "|---:|---:|---:|---:|",
        (
            f"| {pair_summary['wins']} | {pair_summary['ties']} | "
            f"{pair_summary['losses']} | "
            f"{fmt(pair_summary['conditional_win_rate'])} |"
        ),
        "",
    ]

    by_role = defaultdict(list)
    for pair in pairs:
        by_role[pair.get("role", "")].append(pair)
    lines += ["## Win/Tie/Loss By Role", "", "| role | W | T | L | net win |", "|---|---:|---:|---:|---:|"]
    for role, role_pairs in sorted(by_role.items()):
        labels = [classify_pair(p) for p in role_pairs]
        counts = Counter(labels)
        net = (counts["win"] - counts["loss"]) / len(role_pairs)
        lines.append(
            f"| {role or 'unknown'} | {counts['win']} | {counts['tie']} | "
            f"{counts['loss']} | {fmt(net)} |"
        )

    lines += [
        "",
        "## Reliability Slice",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| reliability tasks | {reliability.get('n_tasks', 0)} |",
        f"| delta pass@k | {fmt(reliability.get('delta_pass_at_k', 0.0))} |",
        f"| delta pass^k_rate | {fmt(reliability.get('delta_pass_k_rate', 0.0))} |",
        f"| delta all_pass_k | {fmt(reliability.get('delta_all_pass_k', 0.0))} |",
        "",
        "## Failure Tags",
        "",
        "| failure | control | skill | delta(skill-control) |",
        "|---|---:|---:|---:|",
    ]
    all_tags = sorted(set(failures[CONTROL]) | set(failures[SKILL]))
    for tag in all_tags:
        c = failures[CONTROL][tag]
        s = failures[SKILL][tag]
        lines.append(f"| {tag} | {c} | {s} | {s - c} |")

    if incomplete:
        lines += ["", "## Incomplete Pairs", ""]
        for task_id in sorted(set(incomplete)):
            lines.append(f"- {task_id}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results",
        default="runs/pilot_results.jsonl",
        type=Path,
        help="Path to pilot_results.jsonl",
    )
    parser.add_argument(
        "--experiment",
        default="experiments/agent_skill_pilot.yaml",
        type=Path,
        help="Optional experiment YAML for task metadata",
    )
    parser.add_argument(
        "--pilot-run-id",
        default="",
        help="Optional pilot_run_id filter",
    )
    parser.add_argument("--bootstrap", type=int, default=10_000)
    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    args = parser.parse_args()

    records = filter_records(load_jsonl(args.results), pilot_run_id=args.pilot_run_id)
    task_metadata = load_task_metadata(args.experiment)
    pairs, incomplete = build_main_pairs(records, task_metadata)
    pair_summary = summarize_pairs(pairs, args.bootstrap)
    reliability = summarize_reliability(records)
    failures = summarize_failures(records)

    if args.json:
        print(json.dumps({
            "main": pair_summary,
            "reliability": reliability,
            "failures": {
                CONTROL: dict(failures[CONTROL]),
                SKILL: dict(failures[SKILL]),
            },
            "incomplete_pairs": sorted(set(incomplete)),
        }, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(pair_summary, pairs, reliability, failures, incomplete))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
