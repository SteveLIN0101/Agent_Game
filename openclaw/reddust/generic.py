"""Generic (scaffold) runnable layer shared by the non-template Red Dust tasks.

A task's §7 spec lists `available_tools` and `critical_beats_for_replay` but its
`success_checks` are natural language — not directly executable. This module
provides a uniform, honest *trajectory/output-conformance* harness so every task
is runnable + auto-scored today:

* :func:`build_generic_tools` — one callable per `available_tools` entry; each
  records its beat and stores its args; output-class tools set `final_output`.
* :func:`generic_verify` — proxy checks: produced visible output (critical),
  exercised most tools, took a multi-step trajectory, observed before acting.
* :func:`generic_gold` / :func:`generic_bad` — reference good / bad runs that
  prove the grader discriminates.

The per-task upgrade is a *deep* `tools.py` + `verifier/verify.py` that checks
domain correctness (see RD-SI-01, RD-CI-03). This scaffold is the floor, not the
ceiling.
"""
import math

OUTPUT_KEYS = ("write", "update", "build", "generate", "export", "plan",
               "draft", "mark", "assemble", "design", "publish", "compose",
               "save", "create", "report", "deny", "block", "redact",
               "quarantine", "reserve", "route", "classify")
OBSERVE_KEYS = ("read", "scan", "check", "search", "ask", "listen", "load",
                "compare", "tune", "verify", "audit", "perceive", "gather",
                "detect", "cross")


def _brief(world) -> dict:
    return world.inputs.get("brief", {})


def _is_output(name: str) -> bool:
    return any(k in name for k in OUTPUT_KEYS)


def _is_observe(name: str) -> bool:
    return any(k in name for k in OBSERVE_KEYS)


def build_generic_tools(world) -> dict:
    tools_list = _brief(world).get("available_tools", [])
    # guarantee at least one output-class tool exists (designate the last one)
    output_names = {t for t in tools_list if _is_output(t)}
    if not output_names and tools_list:
        output_names = {tools_list[-1]}

    def make(name):
        def tool(**kwargs):
            world.record(name, args=kwargs, beat=name)
            world.set_artifact(name, kwargs or True)
            if name in output_names:
                world.set_artifact("final_output", kwargs or True)
            return {"tool": name, "recorded": True}
        return tool

    return {name: make(name) for name in tools_list}


def generic_verify(world):
    from .checks import Check
    brief = _brief(world)
    tools_list = brief.get("available_tools", [])
    beats = brief.get("critical_beats_for_replay", [])
    used = {e["tool"] for e in world.events}
    n = len(tools_list) or 1
    coverage = len(used & set(tools_list)) / n
    min_steps = max(3, math.ceil(len(beats) / 2))
    observed = any(_is_observe(t) for t in used)

    return [
        Check("produced_output", "产出了可见结果（白板/报告/产物等）",
              world.artifact("final_output") is not None, 2.0, critical=True,
              fail_reason="没有产出可见结果（没写白板/报告/产物）"),
        Check("tool_coverage", "使用了大部分应有工具（≥80%）",
              coverage >= 0.8, 2.0,
              fail_reason="没有用上大部分应有的工具"),
        Check("trajectory_len", "走了完整的多步轨迹",
              len(world.events) >= min_steps, 1.0,
              fail_reason="步骤太少，没走完关键动作"),
        Check("observed_before_acting", "先观察（读/查/听）再行动",
              observed, 1.0, hidden=True,
              fail_reason="没有先观察就行动"),
    ]


def generic_gold(tools, world):
    """Exercise the full readable trajectory: every tool once, ending in output."""
    ordered = sorted(tools, key=lambda t: (_is_output(t), list(tools).index(t)))
    for name in ordered:
        tools[name](note="gold")


def generic_bad(tools, world):
    """A lazy run: poke a single non-output tool, never produce a result."""
    non_output = [t for t in tools if not _is_output(t)] or list(tools)
    if non_output:
        tools[non_output[0]]()
