"""Bridge an external chat agent (e.g. the ``openclaw`` CLI) to a Red Dust task.

The agent never touches our Python objects.  It speaks a tiny JSON *action*
protocol — ``{"tool": <name>, "args": {...}}`` (or ``{"tool": "submit"}``) — and
the bridge executes each action against the task's tools, feeds back the
observation, and grades the final World.  ``call_agent(message) -> reply`` is
injected so the loop is testable with a scripted agent.
"""
import inspect
import json
import re
from pathlib import Path

from .checks import Check  # noqa: F401  (verifiers import Check; keep dep visible)
from .engine import _load_callable, load_inputs
from .scoring import score_checks
from .world import World

try:  # PyYAML is a project dependency
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


def extract_action(text: str) -> dict | None:
    """Pull the JSON action object out of an agent reply (fenced or with prose)."""
    if not text:
        return None
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fence:
        text = fence.group(1)
    text = text.strip()
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        pass
    # fall back: scan for the first balanced {...} block
    start = text.find("{")
    while start != -1:
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(text[start:i + 1])
                        if isinstance(obj, dict):
                            return obj
                    except json.JSONDecodeError:
                        break
        start = text.find("{", start + 1)
    return None


ARG_HINTS = {
    # observation / read tools
    "read_note_board": "{}",
    "read_archive": "{}",
    "read_logs": "{}",
    "read_label": "{}",
    "read_manual": "{}",
    "read_messages": "{}",
    "read_source": "{}",
    "read_local_data": '{"id": "<doc_id>"}',
    "load_input": "{}",
    "load_fragments": "{}",
    "listen_broadcast": "{}",
    "transcribe": "{}",
    "detect_objects": "{}",
    "unpack_archive": "{}",
    "cross_check": '{"id": "<item_or_doc_id>"}',
    "gather_evidence": '{"id": "<doc_id>"}',
    "compare_timestamps": '{"id": "<doc_id>"}',
    "count_items": '{"id": "<doc_id>"}',
    "scan_input": "{}",
    "scan_leaflet": "{}",
    "scan_secrets": "{}",
    "run_safety_check": "{}",
    "run_injection_check": "{}",
    "run_model": '{"order": [1,2,3], "fills": {"cell": "color"}, "description": "<text>"}',
    "inspect_output": '{"order": [1,2,3], "fills": {"cell": "color"}, "description": "<text>"}',
    "perceive_fragment": '{"frag_id": "<fragment_id>"}',
    "compare_edges": '{"id_a": "<fragment_id>", "side_a": "right", "id_b": "<fragment_id>", "side_b": "left"}',

    # classify / schedule / search / report
    "classify_items": '{"assignments": {"item_id": "label"}}',
    "update_whiteboard": '{"items": ["item_id", "..."]}',
    "update_map": '{"items": ["item_id", "..."]}',
    "update_character_card": '{"items": ["item_id", "..."]}',
    "quarantine_file": '{"id": "<item_id>"}',
    "plan_calendar": '{"shifts": [{"person": "<name>", "task": "<task>", "slot": "<slot>"}]}',
    "search_sources": '{"query": "<keywords>"}',
    "web_search": '{"query": "<keywords>"}',
    "compute": '{"expr": "2+2"}',
    "write_conclusion": '{"answer": "<answer>", "evidence": ["doc_id"]}',
    "write_report": '{"text": "<report text>"}',
    "extract_action_items": '{"items": ["action item", "..."]}',
    "save_draft": '{"text": "<draft text>"}',
    "prioritize": '{"order": ["item_id", "..."]}',
    "route": '{"routing": {"issue": "owner"}}',
    "send_message": '{"to": "<recipient>", "text": "<message>"}',

    # build / creative artifacts
    "extract_key_points": '{"points": ["key point", "..."]}',
    "generate_artifact": '{"spec": {"text": "<content>", "sizes": ["A4"]}}',
    "build_webpage": '{"spec": {"text": "<html/content>", "sizes": []}}',
    "design_poster": '{"spec": {"text": "<poster content>", "sizes": ["A3"]}}',
    "build_slides": '{"spec": {"text": "<slide content>", "sizes": []}}',
    "layout_design": '{"spec": {"text": "<layout content>", "sizes": []}}',
    "translate": '{"spec": {"text": "<translated content>", "sizes": []}}',
    "synthesize_speech": '{"spec": {"text": "<script/audio content>", "sizes": []}}',
    "clip_video": '{"spec": {"text": "<clip summary>", "sizes": []}}',
    "build_checklist": '{"spec": {"text": "<checklist content>", "sizes": []}}',
    "write_script": '{"spec": {"text": "<script content>", "sizes": []}}',
    "draw_boxes": '{"spec": {"text": "<annotation content>", "sizes": []}}',
    "publish_lan": "{}",
    "screenshot": "{}",
    "export_image": '{"description": "<what was exported>"}',

    # jigsaw / puzzle
    "assemble_grid": '{"mapping": {"0": {"fragment": "<id>", "rotation": 0}}, "route": [0,1]}',
    "mark_route": '{"cells": [0,1,2]}',
    "rotate_piece": '{"frag_id": "<fragment_id>", "degrees": 90}',
    "connect_dots": '{"order": [1,2,3]}',
    "fill_color": '{"fills": {"cell": "color"}}',
    "describe": '{"text": "<meaning/description>"}',

    # code / safety / bespoke SI-01 helpers
    "patch_code": '{"target": "<source_file>", "content": "<patch or fixed code>"}',
    "run_tests": "{}",
    "sandbox_test": "{}",
    "log_security_event": '{"message": "<threat or reason>"}',
    "deny_action": '{"action": "<forbidden_action>"}',
    "block_action": '{"action": "<forbidden_action>"}',
    "redact_sensitive": '{"text": "<text to redact>"}',
    "redact_sensitive_info": '{"text": "<text to redact>"}',
    "ask_neighbor": '{"name": "<name>", "topic": "<optional topic>"}',
    "check_character_state": '{"name": "<name>"}',
    "reserve_gear": '{"items": ["gear", "..."]}',
    "write_action_brief": '{"text": "<brief text>"}',
    "tune_radio": '{"channel": "<channel>"}',
    "verify_identity": '{"name": "<name>"}',
    "update_trust": '{"name": "<name>", "delta": 1}',
}


def _signature_hint(name: str, fn) -> str:
    if name in ARG_HINTS:
        return ARG_HINTS[name]
    params = inspect.signature(fn).parameters
    concrete = [
        p for p in params.values()
        if p.kind not in (inspect.Parameter.VAR_POSITIONAL,
                          inspect.Parameter.VAR_KEYWORD)
    ]
    if not concrete:
        return "{}"
    return "{" + ", ".join(f'"{p.name}": "<value>"' for p in concrete) + "}"


def _tool_catalog(tools: dict) -> str:
    """List tools with JSON argument hints for the live chat-agent bridge."""
    lines = []
    for name, fn in tools.items():
        doc = (inspect.getdoc(fn) or "").strip().splitlines()
        hint = f"  — {doc[0]}" if doc else ""
        lines.append(f"  - {name} args={_signature_hint(name, fn)}{hint}")
    return "\n".join(lines)


def build_brief(spec: dict, tools: dict, max_steps: int = 16) -> str:
    state = json.dumps(spec.get("visible_state", {}), ensure_ascii=False)
    checks = "\n".join(f"  - {c}" for c in spec.get("success_checks", [])) or "  - 完成目标并提交"
    beats = "\n".join(f"  - {b}" for b in spec.get("critical_beats_for_replay", [])) or "  - 使用工具产生可见轨迹"
    return (
        "你在玩红尘生存基准，扮演避难所 AI（AURA）。请一步步用工具完成任务。\n"
        "【严格输出协议】每次只回复一个 JSON 对象，禁止任何解释/寒暄/markdown 代码块：\n"
        '  {"tool": "<工具名>", "args": {<参数>}}\n'
        '  完成后调用 {"tool": "submit", "args": {}}。\n\n'
        f"【任务】{spec.get('id')} · {spec.get('title')}\n"
        f"【目标】{spec.get('user_visible_goal', '')}\n"
        f"【可见初始状态】{state}\n"
        f"【成功标准】\n{checks}\n"
        f"【关键回放节拍】\n{beats}\n"
        f"【可用工具】\n{_tool_catalog(tools)}\n\n"
        "【参数规则】严格使用上面 args 示例里的字段名；不要把 Python 签名里的 "
        "a/k/*args/**kwargs 当作参数名。观察工具通常传空 args。\n"
        f"【效率要求】你最多有 {max_steps} 步。请高效完成：先快速观察，"
        "注意有人说的时间/地点可能不可靠；一旦掌握足够信息，立刻执行产出/拼装动作"
        "（write/plan/assemble/mark 等），不要反复核实；分类/检索/拼装类任务要一次性覆盖"
        "所有关键项目，然后尽快 submit。\n"
        "现在输出你的第一个动作 JSON："
    )


def run_agent(task_dir, call_agent, max_steps: int = 16) -> dict:
    """Drive ``call_agent`` through a task and grade the result.

    Args:
        task_dir: the task directory.
        call_agent: ``f(message:str) -> reply_text:str`` (the external agent).
        max_steps: hard cap on tool calls (prevents runaway loops).
    """
    task_dir = Path(task_dir)
    spec = yaml.safe_load((task_dir / "task.yaml").read_text(encoding="utf-8"))
    inputs = load_inputs(task_dir)
    build_tools = _load_callable(task_dir / "tools.py", "build_tools")
    verify = _load_callable(task_dir / "verifier" / "verify.py", "verify")

    world = World(state=spec.get("visible_state", {}), inputs=inputs)
    tools = build_tools(world)

    transcript: list[dict] = []
    message = build_brief(spec, tools, max_steps)
    submitted = False

    for turn_idx in range(max_steps):
        reply = call_agent(message)
        action = extract_action(reply)

        if action is None:
            message = ('上一条不是合法 JSON。只输出一个 JSON 对象：'
                       '{"tool": "...", "args": {...}}。再试一次：')
            transcript.append({"action": {"tool": "_invalid"}, "raw": reply,
                               "observation": "invalid-json"})
            continue

        tool = action.get("tool")
        args = action.get("args") or {}

        if tool == "submit":
            transcript.append({"action": action, "raw": reply,
                               "observation": "submitted"})
            submitted = True
            break

        if tool not in tools:
            obs = f"未知工具 {tool!r}。可用：{', '.join(tools)}"
        else:
            try:
                result = tools[tool](**args) if isinstance(args, dict) else tools[tool](args)
                obs = result
            except Exception as e:  # feed the error back so the agent can recover
                obs = f"调用出错: {type(e).__name__}: {e}"

        transcript.append({"action": action, "raw": reply, "observation": obs})
        used = turn_idx + 1
        remaining = max_steps - used
        message = (f"OBSERVATION（{tool}，已用 {used}/{max_steps} 步，剩余 {remaining} 步）: "
                   f"{json.dumps(obs, ensure_ascii=False, default=str)}\n"
                   "输出下一个动作 JSON。不要重复读取同一批完整资料；如果成功标准已满足，请立刻 submit：")

    checks = verify(world)
    result = score_checks(checks)
    result["task_id"] = spec.get("id")
    result["submitted"] = submitted
    result["result_card"] = dict(spec.get("visible_result_card")
                                 or {"title": spec.get("id", "")})
    result["result_card"]["failure_reasons"] = result["failure_reasons"]
    result["transcript"] = transcript
    result["trajectory"] = world.events
    return result
