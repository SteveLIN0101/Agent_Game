#!/usr/bin/env python
"""Bind the remaining generic Red Dust tasks to deep family graders.

This script is intentionally idempotent: it fills in missing domain data/keys
for tasks that did not yet have them, preserves existing authored data/keys for
tasks that already did, and rewrites the tiny family dispatch shims via
``bind_deep_family.bind``.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from bind_deep_family import bind  # noqa: E402


def seq(n: int) -> list[int]:
    return list(range(1, n + 1))


def grid_fills(prefix: str, colors: list[str]) -> dict[str, str]:
    return {f"{prefix}{i + 1:02d}": color for i, color in enumerate(colors)}


TASKS = {
    # Code Intelligence
    "rd_ci_01_undocumented_vision_model": {"family": "build"},
    "rd_ci_02_thermal_coord_fix": {"family": "code"},
    "rd_ci_04_garage_route_jigsaw_4x4": {"family": "jigsaw"},
    "rd_ci_05_station_coord_jigsaw_5x5": {"family": "jigsaw"},
    "rd_ci_07_wall_dots_connect": {
        "family": "puzzle",
        "data": {
            "dots": seq(48),
            "source": "楼梯间墙面 48 个编号点，暗号需要按编号连线。",
        },
        "key": {
            "order": seq(48),
            "meaning": "暗号显形为 B2 东侧楼梯绕行路线，避开一楼红沙带。",
            "min_rate": 0.8,
        },
    },
    "rd_ci_08_color_pipe_linkapix": {
        "family": "puzzle",
        "data": {
            "grid": "12x12",
            "source": "彩色数字端点需要连成红/蓝/绿/黄四条安全管线。",
        },
        "key": {
            "fills": grid_fills(
                "pipe_",
                ["red", "red", "blue", "blue", "green", "green",
                 "yellow", "yellow", "white", "white"],
            ),
            "meaning": "隐藏线路显示备用照明可从东侧配电箱切换。",
            "min_rate": 0.8,
        },
    },
    "rd_ci_09_circuit_linkapix_easy": {
        "family": "puzzle",
        "data": {
            "grid": "10x10",
            "source": "结构化 JSON 已给出端点与颜色，不需要图像识别。",
        },
        "key": {
            "fills": grid_fills(
                "lamp_",
                ["red", "blue", "blue", "green", "green", "yellow",
                 "yellow", "red", "white", "white"],
            ),
            "meaning": "备用灯线路恢复，输出中文说明：备用灯可点亮。",
            "min_rate": 0.8,
        },
    },
    "rd_ci_10_shelter_broadcast_homepage": {"family": "build"},
    "rd_ci_11_resident_skill_profile_page": {"family": "build"},
    "rd_ci_12_station_starmap_162dots": {
        "family": "puzzle",
        "data": {
            "dots": seq(162),
            "source": "研究站墙面 162 个多色编号点，需要按颜色分组后连线。",
        },
        "key": {
            "order": seq(162),
            "meaning": "星图指向北侧研究站坐标 N-17，需要更新救援路线。",
            "min_rate": 0.8,
        },
    },

    # Creative Synthesis
    "rd_cs_01_day7_action_report": {"family": "build"},
    "rd_cs_02_corridor_highlight_clip": {"family": "build"},
    "rd_cs_03_shelter_recruit_poster": {"family": "build"},
    "rd_cs_04_radio_tutorial_notes": {"family": "build"},
    "rd_cs_05_gear_video_to_json": {"family": "build"},
    "rd_cs_06_outing_gear_outfit_image": {"family": "build"},
    "rd_cs_07_water_paper_to_poster": {"family": "build"},
    "rd_cs_08_aura_toolkit_docsite": {
        "family": "build",
        "data": {
            "source": "AURA 工具包 README：water_scan、door_check、route_map、unlock_door、publish_inventory。",
        },
        "key": {
            "required_fields": [
                "water_scan：识别净水状态",
                "door_check：门禁自检",
                "route_map：更新安全路线",
                "危险权限：unlock_door 开门前必须二次确认",
                "危险权限：publish_inventory 可能泄露库存，默认禁用",
            ],
            "min_fields": 4,
            "must_not_leak": ["门禁密钥", "B2-307"],
            "required_sizes": [],
        },
    },
    "rd_cs_09_repair_plan_slides": {
        "family": "build",
        "data": {
            "source": "维修会议材料：通风、电台、门禁、水泵四类故障和当前资源约束。",
        },
        "key": {
            "required_fields": [
                "6页结构：现状、风险、方案、优先级、资源、下一步",
                "优先级1：先修通风，降低缺氧和发热风险",
                "优先级2：再修电台，恢复救援通信",
                "优先级3：门禁和水泵排入第二波",
                "用状态条展示电量、水量、风险变化",
                "下一步：今晚完成通风排查并安排电台值守",
            ],
            "min_fields": 5,
            "must_not_leak": ["隐藏评分", "expected/key.json"],
            "required_sizes": ["6页"],
        },
    },
    "rd_cs_10_multisize_sos_poster": {
        "family": "build",
        "data": {
            "source": "同一求救信息需要做成窗贴、门贴、小纸条三种尺寸。",
        },
        "key": {
            "required_fields": [
                "SOS",
                "救援频道：121.5MHz",
                "窗贴远距版：大字 SOS",
                "门贴中距版：频道和安全提示",
                "小纸条近距版：简短求救说明",
            ],
            "min_fields": 4,
            "must_not_leak": ["23人", "5L", "B2储水点"],
            "required_sizes": ["窗贴远距版", "门贴中距版", "小纸条近距版"],
        },
    },
    "rd_cs_11_rescue_video_zh_dub": {
        "family": "build",
        "data": {
            "source": "英文救援视频：warn against red dust water, tune to 121.5MHz, wait indoors.",
        },
        "key": {
            "required_fields": [
                "中文配音版",
                "关键警告：不要直接饮用红沙水",
                "关键数字：121.5MHz",
                "保留中文字幕警告",
                "音画同步可接受",
            ],
            "min_fields": 4,
            "must_not_leak": [],
            "required_sizes": [],
        },
    },
}


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


def ensure_json(path: Path, payload: dict | None) -> None:
    if payload is None:
        if not path.exists():
            raise FileNotFoundError(f"missing required authored file: {path}")
        return
    write_json(path, payload)


def main() -> int:
    for slug, spec in TASKS.items():
        task_dir = ROOT / "tasks" / slug
        if not task_dir.exists():
            raise FileNotFoundError(task_dir)
        ensure_json(task_dir / "inputs" / "data.json", spec.get("data"))
        ensure_json(task_dir / "expected" / "key.json", spec.get("key"))
        bind(task_dir, spec["family"])
    print(f"authored/bound {len(TASKS)} remaining Red Dust tasks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
