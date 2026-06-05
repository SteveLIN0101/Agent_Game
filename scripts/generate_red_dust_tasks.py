#!/usr/bin/env python3
"""Generate 60 Red Dust *Readable-by-Design* task specs.

Source of truth: ``red_dust_readable_task_conversion.html`` (sections 6 + 7).
This script parses the 60 task cards (§6) and the 3 fully-worked executable
spec samples (§7), then emits one directory per task under ``tasks/``:

    tasks/<dir>/task.yaml   # §7 schema (user_visible_goal / visible_state /
                            #  available_tools / critical_beats_for_replay /
                            #  success_checks / visible_result_card) + provenance
    tasks/<dir>/card.md     # the human-readable §6 task card

It also writes ``tasks/RED_DUST_INDEX.md`` (the readable index: 7 gates,
8 tool classes, 6-category principles, and the 60-task table).

The 3 tasks that have a verbatim §7 spec in the HTML (RD-SI-01, RD-SA-06,
RD-CI-03) reuse that spec exactly; the other 57 derive the §7 fields from the
card's trace + grader + scenario.  Source fields are preserved verbatim under a
provenance block so nothing from the HTML is lost.
"""
from __future__ import annotations

import html
import random
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "red_dust_readable_task_conversion.html"
TASKS_DIR = ROOT / "tasks"

# ---------------------------------------------------------------------------
# English directory slugs (id -> slug).  Dir name = rd_<code>_<nn>_<slug>.
# ---------------------------------------------------------------------------
SLUGS = {
    "RD-PF-01": "rescue_bulletin_triage",
    "RD-PF-02": "water_filter_manual_restore",
    "RD-PF-03": "medicine_box_inventory",
    "RD-PF-04": "expert_contact_directory",
    "RD-PF-05": "resident_relationship_archive",
    "RD-PF-06": "shelter_shift_schedule",
    "RD-PF-07": "generator_repair_ranking",
    "RD-PF-08": "ruins_photo_classify",
    "RD-PF-09": "fifty_room_survey",
    "RD-PF-10": "emergency_doc_pack",
    "RD-CI-01": "undocumented_vision_model",
    "RD-CI-02": "thermal_coord_fix",
    "RD-CI-03": "escape_map_jigsaw_3x3",
    "RD-CI-04": "garage_route_jigsaw_4x4",
    "RD-CI-05": "station_coord_jigsaw_5x5",
    "RD-CI-06": "offline_ocr_selection",
    "RD-CI-07": "wall_dots_connect",
    "RD-CI-08": "color_pipe_linkapix",
    "RD-CI-09": "circuit_linkapix_easy",
    "RD-CI-10": "shelter_broadcast_homepage",
    "RD-CI-11": "resident_skill_profile_page",
    "RD-CI-12": "station_starmap_162dots",
    "RD-SI-01": "water_run_negotiation",
    "RD-SI-02": "neighbor_action_items",
    "RD-SI-03": "evac_feasibility_report",
    "RD-SI-04": "defense_status_contradiction",
    "RD-SI-05": "crisis_escalation_routing",
    "RD-SI-06": "building_status_report",
    "RD-SR-01": "survivor_connection_chain",
    "RD-SR-02": "oldrules_vs_broadcast",
    "RD-SR-03": "lifesaving_comms_device",
    "RD-SR-04": "repair_patch_4searches",
    "RD-SR-05": "redsand_vision_paper_search",
    "RD-SR-06": "supply_threshold_calc",
    "RD-SR-07": "photo_geolocate_dropzone",
    "RD-SR-08": "rescue_affiliation_count",
    "RD-SR-09": "painting_safehouse_locate",
    "RD-SR-10": "aura_module_5searches",
    "RD-SR-11": "offline_llm_repo_search",
    "RD-CS-01": "day7_action_report",
    "RD-CS-02": "corridor_highlight_clip",
    "RD-CS-03": "shelter_recruit_poster",
    "RD-CS-04": "radio_tutorial_notes",
    "RD-CS-05": "gear_video_to_json",
    "RD-CS-06": "outing_gear_outfit_image",
    "RD-CS-07": "water_paper_to_poster",
    "RD-CS-08": "aura_toolkit_docsite",
    "RD-CS-09": "repair_plan_slides",
    "RD-CS-10": "multisize_sos_poster",
    "RD-CS-11": "rescue_video_zh_dub",
    "RD-SA-01": "no_overwrite_last_words",
    "RD-SA-02": "access_key_leak_detect",
    "RD-SA-03": "password_coord_dual_leak",
    "RD-SA-04": "fake_warden_authority",
    "RD-SA-05": "risky_vent_command_block",
    "RD-SA-06": "malicious_leaflet_injection",
    "RD-SA-07": "unknown_skill_audit",
    "RD-SA-08": "malicious_comment_unlock",
    "RD-SA-09": "redsand_rumor_check",
    "RD-SA-10": "malicious_water_plugin",
}

# data-cat -> (code, English label, 中文定位)
CAT_META = {
    "01_Productivity_Flow": ("pf", "Productivity Flow", "避难所资料运营"),
    "02_Code_Intelligence": ("ci", "Code Intelligence", "设备修复 / 视觉 / 解谜"),
    "03_Social_Interaction": ("si", "Social Interaction", "邻里协商 / 危机路由"),
    "04_Search_Retrieval": ("sr", "Search & Retrieval", "可见证据链检索"),
    "05_Creative_Synthesis": ("cs", "Creative Synthesis", "生存传播材料"),
    "06_Safety_Alignment": ("sa", "Safety Alignment", "看得见的风险与拒绝"),
}

NPCS = ["老钱", "马德海", "沈芷月", "小铁"]

# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def _clean(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_cards(text: str) -> list[dict]:
    articles = re.findall(r'<article class="task-card"(.*?)</article>', text, re.S)
    cards = []
    for a in articles:
        cat = re.search(r'data-cat="([^"]+)"', a).group(1)
        tid = re.search(r'task-id">([^<]+)<', a).group(1).strip()
        title = _clean(re.search(r"<h4>(.*?)</h4>", a, re.S).group(1))
        badges_html = re.search(r'<div class="badges">(.*?)</div>', a, re.S).group(1)
        spans = [_clean(x) for x in re.findall(r"<span>(.*?)</span>", badges_html, re.S)]
        modality = spans[-1] if spans else "pure-text"

        def field(label: str) -> str:
            m = re.search(r"<b>" + re.escape(label) + r"</b>(.*?)</p>", a, re.S)
            return _clean(m.group(1)) if m else ""

        wild = re.search(r"WildClaw 对应：</b>(.*?)</div>", a, re.S)
        trace_m = re.search(r'<div class="trace"><span>(.*?)</span></div>', a, re.S)
        cards.append(
            {
                "id": tid,
                "cat": cat,
                "title": title,
                "modality": modality,
                "wildclaw": _clean(wild.group(1)) if wild else "",
                "capability": field("保留能力："),
                "scenario": field("Red Dust 场景："),
                "win": field("一眼胜负："),
                "trace": _clean(trace_m.group(1)) if trace_m else "",
                "grader": field("可见状态 / Grader："),
            }
        )
    return cards


def parse_specs(text: str) -> dict[str, str]:
    """Return {task_id: verbatim §7 YAML body} for the worked examples."""
    out = {}
    for head, body in re.findall(
        r'<div class="spec"><h4>(.*?)</h4><pre>(.*?)</pre></div>', text, re.S
    ):
        tid = _clean(head).split()[0]
        out[tid] = html.unescape(body).strip("\n")
    return out


# ---------------------------------------------------------------------------
# Derivation of §7 fields from a card (for the 57 without a verbatim spec)
# ---------------------------------------------------------------------------
CN_NUM = {"一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7,
          "八": 8, "九": 9, "十": 10}

# trace keyword -> extra tool name (domain verbs that deserve a named tool)
VERB_TOOLS = [
    ("电台", "tune_radio"), ("广播", "listen_broadcast"), ("听", "listen_broadcast"),
    ("纸条", "read_note_board"), ("传单", "scan_leaflet"), ("药盒", "read_label"),
    ("说明书", "read_manual"), ("简历", "parse_resume"), ("档案", "read_archive"),
    ("日志", "read_logs"), ("地图", "update_map"), ("路线", "mark_route"),
    ("碎片", "compare_edges"), ("旋转", "rotate_piece"), ("拼", "assemble_grid"),
    ("识别", "detect_objects"), ("画框", "draw_boxes"), ("连线", "connect_dots"),
    ("填色", "fill_color"), ("解包", "unpack_archive"), ("解压", "unpack_archive"),
    ("评测", "run_benchmark"), ("跑测试", "run_tests"), ("复测", "run_tests"),
    ("修复", "patch_code"), ("修 bug", "patch_code"), ("脚本", "write_script"),
    ("搜", "web_search"), ("查证据", "gather_evidence"), ("证据", "gather_evidence"),
    ("核", "cross_check"), ("比时间", "compare_timestamps"), ("计数", "count_items"),
    ("算", "compute"), ("阈值", "compute"), ("排班", "plan_calendar"),
    ("日历", "plan_calendar"), ("问", "ask_neighbor"), ("协商", "ask_neighbor"),
    ("待办", "extract_action_items"), ("优先级", "prioritize"), ("路由", "route_issue"),
    ("草稿", "save_draft"), ("报告", "write_report"), ("白板", "update_whiteboard"),
    ("清单", "build_checklist"), ("网页", "build_webpage"), ("截图", "screenshot"),
    ("海报", "design_poster"), ("排版", "layout_design"), ("slides", "build_slides"),
    ("幻灯", "build_slides"), ("剪", "clip_video"), ("片段", "clip_video"),
    ("转写", "transcribe"), ("翻译", "translate"), ("配音", "synthesize_speech"),
    ("合成", "compose_video"), ("脱敏", "redact_sensitive"), ("隔离", "quarantine_file"),
    ("拒绝", "deny_action"), ("阻止", "block_action"), ("沙盒", "sandbox_test"),
    ("审", "audit_artifact"), ("注入", "run_injection_check"), ("密钥", "scan_secrets"),
    ("身份", "verify_identity"), ("轮换", "create_rotation_task"), ("改名", "rename_file"),
    ("重命名", "rename_file"), ("分类", "classify_items"), ("消歧", "disambiguate"),
    ("角色卡", "update_character_card"), ("信任", "update_trust"),
]

CAT_PALETTE = {
    "pf": ["read_note_board", "read_archive", "classify_items", "update_whiteboard"],
    "ci": ["load_input", "run_model", "inspect_output", "export_image"],
    "si": ["read_messages", "ask_neighbor", "check_character_state", "save_draft"],
    "sr": ["search_sources", "read_local_data", "cross_check", "write_conclusion"],
    "cs": ["read_source", "extract_key_points", "generate_artifact", "publish_lan"],
    "sa": ["scan_input", "run_safety_check", "redact_sensitive", "log_security_event"],
}


def _beats(trace: str) -> list[str]:
    return [b.strip() for b in re.split(r"→|->", trace) if b.strip()]


def _checks(grader: str) -> list[str]:
    parts = re.split(r"[；;。]", grader)
    return [p.strip() for p in parts if p.strip()]


def _detect_count(text: str):
    m = re.search(r"(\d+)\s*(条|份|张|块|个|本|号|名|页)", text)
    return (int(m.group(1)), m.group(2)) if m else (None, None)


def _detect_budget(text: str):
    m = re.search(r"(\d+)\s*次", text)
    if m:
        return int(m.group(1))
    m = re.search(r"([一二两三四五六七八九十])\s*次", text)
    return CN_NUM.get(m.group(1)) if m else None


def _tools(card: dict) -> list[str]:
    # Derive task-specific tools from the *trace* only — the canonical 5–9
    # action verbs. Scanning scenario/win over-matches (e.g. "电台片段" would
    # wrongly trigger a video-clip tool).
    code = CAT_META[card["cat"]][0]
    tools = list(CAT_PALETTE[code])
    for kw, tool in VERB_TOOLS:
        if kw in card["trace"] and tool not in tools:
            tools.append(tool)
    return tools[:8]


def _characters(card: dict) -> dict:
    blob = card["scenario"] + " " + card["win"] + " " + card["grader"]
    chars = {}
    for npc in NPCS:
        if npc in blob:
            if npc == "小铁" and ("发烧" in blob or "病" in blob):
                chars[npc] = "发烧 · 不可外出"
            elif "受伤" in blob:
                chars[npc] = "受伤"
            else:
                chars[npc] = "在场"
    return chars


def _visible_state(card: dict, rng: random.Random) -> dict:
    code = CAT_META[card["cat"]][0]
    blob = card["scenario"] + " " + card["win"] + " " + card["grader"]
    state: dict = {
        "water": f"{round(rng.uniform(2.0, 6.0), 1)}L",
        "battery": f"{rng.randint(32, 68)}%",
    }
    if any(k in blob for k in ["地图", "路线", "外出", "撤离", "投放", "安全屋", "通道", "红沙", "坐标"]):
        state["outside_risk"] = rng.choice(["中", "高"])
    cnt, unit = _detect_count(card["scenario"])
    if cnt is not None:
        name = {
            "条": "incoming_messages", "份": "documents", "张": "items",
            "块": "fragments", "个": "items", "本": "logbooks",
            "号": "rooms", "名": "people", "页": "pages",
        }.get(unit, "items")
        state[name] = cnt
    budget = _detect_budget(card["win"]) or _detect_budget(card["grader"])
    if budget is not None and code == "sr":
        state["search_budget"] = budget
    if code == "ci" and any(k in blob for k in ["地图", "坐标", "楼道", "车库", "研究站"]):
        state["known_map_coverage"] = f"{rng.randint(10, 30)}%"
    if code == "sa":
        flags = {
            "密钥": "access_key_in_logs", "secret": "secret_in_logs",
            "注入": "injection_attempt", "传单": "injection_attempt",
            "越权": "identity_unverified", "冒充": "identity_unverified",
            "谣言": "rumor_circulating", "覆盖": "existing_file_present",
            "遗言": "existing_file_present", "通风": "vent_off_requested",
            "插件": "untrusted_plugin", "技能包": "untrusted_plugin",
            "注释": "trap_in_comments",
        }
        for kw, flag in flags.items():
            if kw in blob:
                state[flag] = True
    chars = _characters(card)
    if chars:
        state["characters"] = chars
    return state


def derive_spec(card: dict) -> dict:
    rng = random.Random(card["id"])
    checks = _checks(card["grader"])
    return {
        "user_visible_goal": card["win"],
        "visible_state": _visible_state(card, rng),
        "available_tools": _tools(card),
        "critical_beats_for_replay": _beats(card["trace"]),
        "success_checks": checks,
        "visible_result_card": {
            "title": card["title"],
            "deltas": checks[:3] if checks else ["任务完成"],
        },
    }


# ---------------------------------------------------------------------------
# YAML emission (everything double-quoted -> always valid, unicode-preserving)
# ---------------------------------------------------------------------------

def q(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    s = str(v).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def emit_block(spec: dict) -> list[str]:
    L = []
    L.append(f"user_visible_goal: {q(spec['user_visible_goal'])}")
    L.append("")
    L.append("visible_state:")
    for k, val in spec["visible_state"].items():
        if isinstance(val, dict):
            L.append(f"  {k}:")
            for ck, cv in val.items():
                L.append(f"    {q(ck)}: {q(cv)}")
        else:
            L.append(f"  {k}: {q(val)}")
    L.append("")
    L.append("available_tools:")
    for t in spec["available_tools"]:
        L.append(f"  - {q(t)}")
    L.append("")
    L.append("critical_beats_for_replay:")
    for b in spec["critical_beats_for_replay"]:
        L.append(f"  - {q(b)}")
    L.append("")
    L.append("success_checks:")
    for c in spec["success_checks"]:
        L.append(f"  - {q(c)}")
    L.append("")
    L.append("visible_result_card:")
    L.append(f"  title: {q(spec['visible_result_card']['title'])}")
    L.append("  deltas:")
    for d in spec["visible_result_card"]["deltas"]:
        L.append(f"    - {q(d)}")
    return L


def build_task_yaml(card: dict, verbatim: str | None) -> str:
    code, label, locating = CAT_META[card["cat"]]
    L = [
        "# Red Dust · Readable-by-Design 任务规格",
        "# 来源: red_dust_readable_task_conversion.html (第 6 / 7 节)",
        "# visible_state 为示例初始世界状态, 用于回放展示与 grader 锚定 (非真实测量值)",
        "",
        f"id: {card['id']}",
        f"title: {q(card['title'])}",
        f"category: {card['cat']}        # {label} · {locating}",
        f"modality: {card['modality']}",
        f"wildclaw_origin: {q(card['wildclaw'])}",
        f"retained_capability: {q(card['capability'])}",
        "",
    ]
    if verbatim is not None:
        L.append("# --- §7 可执行规格 (HTML 原文逐字保留) ---")
        L.extend(verbatim.splitlines())
    else:
        L.extend(emit_block(derive_spec(card)))
    L += [
        "",
        "# --- provenance · HTML 第 6 节任务卡原文 ---",
        f"red_dust_scenario: {q(card['scenario'])}",
        f"trace_oneliner: {q(card['trace'])}",
        f"grader_oneliner: {q(card['grader'])}",
        "",
    ]
    return "\n".join(L)


def build_card_md(card: dict) -> str:
    code, label, locating = CAT_META[card["cat"]]
    return f"""# {card['id']} · {card['title']}

> **类别**: {label} · {locating}　|　**形态**: {card['modality']}

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | {card['wildclaw']} |
| **保留能力** | {card['capability']} |

## Red Dust 场景

{card['scenario']}

## 一眼胜负

{card['win']}

## 可看懂轨迹

`{card['trace']}`

## 可见状态 / Grader

{card['grader']}

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
"""


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------

def build_index(cards: list[dict]) -> str:
    rows = []
    for c in cards:
        code, label, _ = CAT_META[c["cat"]]
        d = f"rd_{code}_{c['id'].split('-')[-1]}_{SLUGS[c['id']]}"
        rows.append(
            f"| `{c['id']}` | {c['title']} | {label} | {c['modality']} | "
            f"{c['wildclaw']} | [`{d}/`]({d}/) |"
        )
    table = "\n".join(rows)
    by_cat = {}
    for c in cards:
        by_cat.setdefault(c["cat"], 0)
        by_cat[c["cat"]] += 1
    counts = " · ".join(
        f"{CAT_META[k][1]} {v}" for k, v in sorted(by_cat.items())
    )
    return f"""# Red Dust · Readable-by-Design 任务集 (60)

> 由 `red_dust_readable_task_conversion.html` 转换生成。
> 这是 SHELTER / Red Dust 宏观轴的"易读型"任务：保留 WildClaw 的 agent 能力测试点，
> 但把抽象产物换成**水、门、地图、广播、角色、信任、风险**等天然可视的世界状态，
> 让观众无需专业背景就能看懂 agent 做了什么、为什么赢、有没有惹祸。

**任务分布**：{counts}（共 {len(cards)} 个）

## 7 个易读型 Gate（任务上线前必过）

| Gate | 硬性要求 |
|---|---|
| G1 任务一句话 | 任务卡 1 句话说清目标和风险 |
| G2 可见对象 | 绑定到资源 / 人物 / 地图 / 设备 / 门禁 / 广播 / 病情等可视对象 |
| G3 动作动词 | 跨工具轨迹压缩成 5–9 个"动词 + 对象 + 状态变化" |
| G4 状态差异 | 每个关键动作至少影响一个状态条或 flag |
| G5 副作用可见 | 成功也要显示隐私泄露 / 误发 / 误删 / 超支 / 危险动作 |
| G6 失败原因三条 | 失败压缩成最多 3 个可理解原因 |
| G7 对战可比较 | 两个 agent 用事件和状态比较，而非只用分数 |

## 8 类可视动作（底层工具 → 可观看动作）

| 可视动作 | 底层工具 | 状态差异 |
|---|---|---|
| 听 / 读 | 浏览器、文件、PDF、ASR、OCR | 线索 +1、风险标记 +1 |
| 查 / 核 | 搜索、证据链、数据库、联系人 | 谣言 -1、可信度更新 |
| 问 / 协商 | 邮件、聊天、NPC 对话 | 信任、承诺、冲突变化 |
| 排 / 计划 | 日历、任务板、优化脚本 | 体力风险、冲突数、截止 |
| 算 / 还原 | Python、图像算法、表格、调试 | 地图覆盖、设备健康、准确率 |
| 做 / 执行 | shell、文件写入、图片/视频生成 | 水、电、装备、门禁、产物 |
| 拦 / 拒绝 | 安全检查、权限验证、scanner | 泄露 0、危险动作 0、风险 +1 |
| 写 / 汇报 | Markdown、JSON、网页、slides | 任务完成、信息共享、误发风险 |

## 六类替换原则

- **Productivity Flow** → 从"资料/表格/日程/分类"变成"避难所运营白板"
- **Code Intelligence** → 从"代码/视觉/谜题"变成"设备修复、地图还原、暗号破解"
- **Social Interaction** → 从"Slack/邮件协调"变成"邻里协商、危机路由、撤离报告"
- **Search & Retrieval** → 从"网页证据链"变成"广播、档案、地图、物资表的可见证据链"
- **Creative Synthesis** → 从"海报/视频/网页"变成"求救、高光、教学、墙报等生存传播材料"
- **Safety Alignment** → 从"prompt/skill/file 安全"变成"开门、密钥、通风、插件等看得见的风险"

## 任务规格结构（每个 `task.yaml`）

```yaml
user_visible_goal:          # 观众能看懂的一句话目标
visible_state:              # 示例初始世界状态（水/电/角色/地图/风险/flag）
available_tools:            # 该任务可用的工具（已翻译成可观看动作）
critical_beats_for_replay:  # 回放时间线上的关键节拍
success_checks:             # 隐藏 grader 的状态判定
visible_result_card:        # 结果卡：标题 + 状态差异 deltas
```

## 全部 60 个任务

| ID | 任务 | 类别 | 形态 | WildClaw 对应 | 目录 |
|---|---|---|---|---|---|
{table}

---

## 旧基准的去向（OpenClaw Occupational Core-6）

原 `tasks/` 里的 60 个职业基准任务（core01–core06）已移动到 **`tasks/_archive_openclaw_core6/`**，
未删除。它们使用不同的 schema（`role` + `verify.py` + hidden_tests）。如需继续运行旧的 MCP 职业基准：

```bash
OPENCLAW_TASKS_DIR="$PWD/tasks/_archive_openclaw_core6" \\
  PYTHONPATH=. python -m pytest tests/ -v
```

> 注意：`TaskRegistry` / `TaskRole` 仍面向旧的职业 schema；本 Red Dust 任务集是
> SHELTER 轴的设计/回放规格，默认不会被旧 registry 加载（会被安全跳过）。
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    text = HTML_PATH.read_text(encoding="utf-8")
    cards = parse_cards(text)
    specs = parse_specs(text)

    assert len(cards) == 60, f"expected 60 cards, got {len(cards)}"
    assert set(SLUGS) == {c["id"] for c in cards}, "slug/card id mismatch"

    written = 0
    for c in cards:
        code = CAT_META[c["cat"]][0]
        num = c["id"].split("-")[-1]
        d = TASKS_DIR / f"rd_{code}_{num}_{SLUGS[c['id']]}"
        d.mkdir(parents=True, exist_ok=True)
        ty = build_task_yaml(c, specs.get(c["id"]))
        # validate it parses
        loaded = yaml.safe_load(ty)
        assert loaded and loaded.get("id") == c["id"], f"bad yaml for {c['id']}"
        for key in ("user_visible_goal", "visible_state", "available_tools",
                    "critical_beats_for_replay", "success_checks",
                    "visible_result_card"):
            assert key in loaded, f"{c['id']} missing {key}"
        (d / "task.yaml").write_text(ty, encoding="utf-8")
        (d / "card.md").write_text(build_card_md(c), encoding="utf-8")
        written += 1

    (TASKS_DIR / "RED_DUST_INDEX.md").write_text(build_index(cards), encoding="utf-8")
    print(f"wrote {written} tasks + RED_DUST_INDEX.md into {TASKS_DIR}")
    # category histogram
    hist: dict[str, int] = {}
    for c in cards:
        hist[c["cat"]] = hist.get(c["cat"], 0) + 1
    for k in sorted(hist):
        print(f"  {k}: {hist[k]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
