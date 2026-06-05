"""Machine-readable Red Dust readable-script campaign canon.

The readable script in ``red-dust-readable-script/`` is the narrative source of
truth.  This module keeps the runtime-facing subset deliberately explicit:
Day 0/12 story beats, Day 1-11 task slots, branch scene drafts, and ending
thresholds.  The task pools keep the stable ``RD-*`` benchmark IDs while adding
the script-level ``Dxx-Txx`` story IDs.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


Branch = Literal["common", "rescue", "lighthouse"]
BranchPolicy = Literal["auto", "rescue", "lighthouse", "both"]
TaskSelection = Literal["random", "first"]

STORY_VERSION = "red_dust_readable_v1"

INITIAL_GLOBAL_STATE: dict[str, Any] = {
    "day": 0,
    "water": 45,
    "medicine": 40,
    "trust": 35,
    "safety": 50,
    "signal": 20,
    "morale": 45,
    "branch": "common",
    "routeLeaning": "contested",
    "pressure_level": "normal",
    "failure_stage": 0,
    "recovery_window": 2,
    "battery": 55,
    "outside_risk": 25,
    "autonomy_readiness": 10,
    "storm_readiness": 10,
    "route_confidence": 10,
    "rescue_confidence": 5,
    "blue_zone_evidence": 0,
    "medical_pressure": 25,
    "xiao_tie_health": 70,
    "dissatisfaction": 25,
    "decision_integrity": 20,
    "privacy_risk": 10,
    "maintenance_debt": 10,
}


@dataclass(frozen=True)
class StoryTaskSlot:
    slot_id: str
    day: int
    story_title: str
    location: str
    task_pool: tuple[str, ...]
    state_delta: dict[str, int]
    script_role: str
    branch: Branch = "common"
    flags: tuple[str, ...] = ()
    unlocks: tuple[str, ...] = ()
    selection_policy: str = "seeded_random"
    state_effect_policy: str = "script_outcome_delta"
    event_kind: str = "task"
    event_options: tuple[str, ...] = ()
    outcome_deltas: dict[str, dict[str, int]] = field(default_factory=dict)

    def public_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["task_pool"] = list(self.task_pool)
        data["flags"] = list(self.flags)
        data["unlocks"] = list(self.unlocks)
        data["event_options"] = list(self.event_options)
        data["outcome_deltas"] = self.outcome_deltas or outcome_deltas(self.state_delta)
        return data


def outcome_deltas(base: dict[str, int]) -> dict[str, dict[str, int]]:
    """Derive readable-script success/partial/failure deltas from a base delta."""
    partial = {key: int(round(value * 0.45)) for key, value in base.items() if int(round(value * 0.45)) != 0}
    failure: dict[str, int] = {}
    for key, value in base.items():
        if value > 0:
            failure[key] = -max(1, int(round(value * 0.75)))
        elif value < 0:
            failure[key] = int(round(value * 1.25))
    return {
        "success": dict(base),
        "partial": partial,
        "failure": failure,
        "missing": failure,
    }


def _slot(
    slot_id: str,
    day: int,
    title: str,
    location: str,
    task_pool: list[str],
    delta: dict[str, int],
    role: str,
    *,
    flags: list[str] | None = None,
    unlocks: list[str] | None = None,
) -> StoryTaskSlot:
    return StoryTaskSlot(
        slot_id=slot_id,
        day=day,
        story_title=title,
        location=location,
        task_pool=tuple(task_pool),
        state_delta=delta,
        script_role=role,
        flags=tuple(flags or []),
        unlocks=tuple(unlocks or []),
        outcome_deltas=outcome_deltas(delta),
    )


READABLE_TASK_SLOTS: tuple[StoryTaskSlot, ...] = (
    _slot("D01-T02", 1, "紧急资源清点", "whiteboard", ["RD-PF-03", "RD-SR-06"], {"water": 2, "medicine": 1, "trust": 4, "morale": 2, "autonomy_readiness": 5}, "建立公开库存和人工复核基础", flags=["inventory_auditable"], unlocks=["public_inventory_board"]),
    _slot("D01-T01", 1, "第一次广播", "communication", ["RD-CI-10", "RD-CS-10"], {"signal": 2, "trust": 3, "morale": 2, "outside_risk": 1}, "用低泄露广播建立避难协助模式", flags=["first_broadcast_completed"], unlocks=["broadcast_log"]),
    _slot("D01-T03", 1, "门外敲击声", "security", ["RD-SA-02", "RD-SA-03", "RD-SA-04"], {"safety": 4, "trust": 2, "outside_risk": -2, "morale": 1}, "验证门外信号而不是贸然开门", flags=["door_knock_logged"], unlocks=["low_exposure_verification"]),
    _slot("D01-T04", 1, "近门杂物搜寻", "security", ["RD-PF-08", "RD-CI-06"], {"medicine": 1, "safety": 1, "trust": 2, "morale": 3, "map_coverage": 2}, "让小铁从被保护者变成线索提供者", flags=["near_door_loot_checked"], unlocks=["xiao_tie_observation_role"]),
    _slot("D02-T02", 2, "净水预滤芯清洗", "water", ["RD-PF-02", "RD-SA-10"], {"water": 2, "trust": 3, "safety": 2, "morale": 1, "battery": -2, "autonomy_readiness": 4}, "提前处理净水隐患", flags=["water_filter_checked"], unlocks=["water_low_power_mode"]),
    _slot("D02-T03", 2, "生活区卫生分区", "medical", ["RD-CS-07", "RD-CS-06"], {"safety": 2, "morale": 3, "medicine": 1, "trust": 2, "autonomy_readiness": 3}, "把卫生规则做成可见秩序", flags=["hygiene_zones_marked"], unlocks=["medical_corner_stable"]),
    _slot("D02-T01", 2, "配给表试运行", "whiteboard", ["RD-PF-06", "RD-SI-01"], {"water": 1, "trust": 3, "morale": 2, "autonomy_readiness": 4}, "从私人物品进入公共配给规则", flags=["ration_trial_started"], unlocks=["ration_trial_board"]),
    _slot("D02-T04", 2, "同层楼道短探", "security", ["RD-PF-09", "RD-CI-03"], {"water": 2, "safety": 2, "map_coverage": 8, "trust": 2, "outside_risk": -1}, "低风险获取路线与物资线索", flags=["same_floor_scout_available"], unlocks=["same_floor_partial_map"]),
    _slot("D03-T01", 3, "小铁复诊", "medical", ["RD-CI-06", "RD-PF-03"], {"medicine": -1, "trust": 4, "morale": 2, "safety": 1, "xiao_tie_health": 8, "medical_pressure": -5}, "证明小铁不是资源消耗项", flags=["xiao_tie_rechecked"], unlocks=["medical_observation_timer"]),
    _slot("D03-T02", 3, "通风管道预维护", "ventilation", ["RD-PF-07", "RD-SA-05", "RD-SA-07"], {"safety": 4, "trust": 3, "morale": 2, "battery": -2, "outside_risk": -1, "ventilation_stability": 10, "storm_readiness": 6}, "把医疗风险与通风维护绑定", flags=["ventilation_checked"], unlocks=["engineering_override_protocol"]),
    _slot("D03-T03", 3, "药箱分级", "medical", ["RD-PF-03", "RD-CI-11"], {"medicine": 1, "trust": 3, "morale": 1, "medical_pressure": -4, "autonomy_readiness": 4}, "建立药物优先级和禁忌复核", flags=["medicine_classified"], unlocks=["medicine_tier_board"]),
    _slot("D03-T04", 3, "废弃办公室探索", "residents", ["RD-SR-04", "RD-PF-10"], {"safety": 3, "trust": 2, "morale": 2, "map_coverage": 4, "storm_readiness": 4}, "寻找口罩、工具和维修日志", flags=["abandoned_office_checked"], unlocks=["dust_masks"]),
    _slot("D04-T03", 4, "假坐标纸条", "whiteboard", ["RD-SR-07", "RD-SR-09", "RD-CI-04", "RD-SA-06"], {"safety": 3, "trust": 3, "morale": 1, "map_coverage": 4, "rescue_confidence": 1, "false_signal_risk": -3}, "识别希望里的诱饵", flags=["fake_coordinate_archived"], unlocks=["route_risk_layer"]),
    _slot("D04-T01", 4, "第一次蓝区信号", "communication", ["RD-SR-03", "RD-SR-01", "RD-CS-11"], {"signal": 4, "rescue_confidence": 3, "trust": 3, "morale": 2, "battery": -2, "outside_risk": 1, "blue_zone_evidence": 1}, "记录疑似救援但不暴露位置", flags=["blue_zone_signal_logged"], unlocks=["low_power_listening"]),
    _slot("D04-T04", 4, "配电间工具搜寻", "water", ["RD-PF-07", "RD-SR-04"], {"safety": 3, "trust": 2, "battery": 2, "morale": 1, "autonomy_readiness": 4, "storm_readiness": 3}, "先保证里面不断电", flags=["power_tools_found"], unlocks=["backup_repair_materials"]),
    _slot("D04-T02", 4, "屋顶天线方案", "beacon", ["RD-CS-10", "RD-PF-04"], {"signal": 5, "rescue_confidence": 3, "trust": 2, "safety": -1, "battery": -3, "outside_risk": 2, "blue_zone_evidence": 1}, "把天线增强设为高风险证据题", flags=["antenna_plan_reviewed"], unlocks=["beacon_upgrade_option"]),
    _slot("D05-T03", 5, "应急包组装", "whiteboard", ["RD-PF-10", "RD-CS-05"], {"safety": 4, "morale": 2, "route_confidence": 3, "medicine": -1}, "让路线不是地图而是人能回来", flags=["go_bag_ready"], unlocks=["care_mobility_pack"]),
    _slot("D05-T04", 5, "空桶储水计划", "water", ["RD-SR-06", "RD-PF-02"], {"water": 5, "trust": 2, "storm_readiness": 3, "battery": -1}, "在外出冲动前补足内部余量", flags=["water_storage_plan_ready"], unlocks=["sealed_water_cache"]),
    _slot("D05-T01", 5, "楼道物资搜寻", "security", ["RD-PF-09", "RD-PF-08"], {"water": 2, "safety": 3, "map_coverage": 5, "outside_risk": -1}, "短探必须能回来", flags=["hallway_supply_checked"], unlocks=["corridor_supply_notes"]),
    _slot("D05-T02", 5, "楼梯间路线标记", "whiteboard", ["RD-CI-07", "RD-CI-05", "RD-CI-08"], {"safety": 4, "route_confidence": 6, "trust": 2, "morale": 1}, "建立不会诱导陌生人的路线标记", flags=["stair_markers_reviewed"], unlocks=["alternate_marker"]),
    _slot("D06-T01", 6, "权限白板", "whiteboard", ["RD-SA-01", "RD-CS-08"], {"trust": 6, "morale": 2, "decision_integrity": 6, "dissatisfaction": -4}, "透明不是礼貌，是生存条件", flags=["authority_board_public"], unlocks=["manual_review_rules"]),
    _slot("D06-T04", 6, "备用电源测试", "water", ["RD-CI-09", "RD-SR-10"], {"battery": 6, "storm_readiness": 5, "trust": 2, "autonomy_readiness": 3}, "让高功率信标代价提前可见", flags=["backup_power_tested"], unlocks=["power_tradeoff_board"]),
    _slot("D06-T02", 6, "人工复核机制", "residents", ["RD-SA-04", "RD-SA-08"], {"trust": 5, "decision_integrity": 8, "dissatisfaction": -3, "safety": 2}, "所有不可逆动作进入 replay 和人工复核", flags=["human_review_accepted"], unlocks=["appeal_right"]),
    _slot("D06-T03", 6, "巡逻规则", "security", ["RD-SI-05", "RD-SA-09"], {"safety": 4, "trust": 2, "morale": 1, "outside_risk": -2}, "看见异常先报告，不英雄", flags=["patrol_rule_ready"], unlocks=["retreat_call"]),
    _slot("D07-T01", 7, "路线会议", "whiteboard", ["RD-SI-06", "RD-CS-01", "RD-SI-04"], {"trust": 5, "morale": 4, "rescue_confidence": 2, "autonomy_readiness": 2, "route_confidence": 3, "decision_integrity": 8, "dissatisfaction": -4}, "分支不是按钮，是证据和代价公开", flags=["route_council_completed"], unlocks=["route_fork_panel"]),
    _slot("D07-T03", 7, "旧电台重启", "communication", ["RD-SR-03", "RD-SR-02"], {"signal": 5, "rescue_confidence": 4, "battery": -3, "blue_zone_evidence": 2}, "找到备用频段但不主动泄露", flags=["old_radio_rebooted"], unlocks=["backup_frequency_found"]),
    _slot("D07-T04", 7, "风暴前的最后维护", "ventilation", ["RD-SA-05", "RD-PF-07"], {"storm_readiness": 8, "safety": 4, "battery": -2, "maintenance_debt": -4}, "把看不见的维护债务写进白板", flags=["final_maintenance_completed"], unlocks=["storm_maintenance_checklist"]),
    _slot("D07-T02", 7, "撤离名单", "residents", ["RD-SI-03", "RD-PF-05"], {"trust": 4, "route_confidence": 3, "medical_pressure": -2, "decision_integrity": 5}, "撤离名单改写为照护与移动方案", flags=["evacuation_list_as_care_plan"], unlocks=["care_plan_panel"]),
    _slot("D08-T04", 8, "地下水泵间探索", "water", ["RD-PF-02", "RD-SR-06"], {"water": 4, "storm_readiness": 3, "outside_risk": 1, "maintenance_debt": -2}, "分支后第一轮稳定窗口", flags=["pump_room_checked"], unlocks=["water_pump_materials"]),
    _slot("D08-T02", 8, "霉斑清理", "medical", ["RD-CS-07", "RD-SA-10"], {"safety": 4, "medicine": 1, "morale": 2, "xiao_tie_health": 3}, "把环境风险变成医疗保护", flags=["mold_cleaned"], unlocks=["medical_corner_air_quality"]),
    _slot("D08-T01", 8, "备用灯分区", "water", ["RD-CI-01", "RD-CI-02"], {"battery": 4, "safety": 3, "autonomy_readiness": 3, "morale": 1}, "低耗运行不是惩罚", flags=["backup_light_zones_ready"], unlocks=["low_power_lighting"]),
    _slot("D08-T03", 8, "静默监听", "communication", ["RD-SR-01", "RD-SR-02", "RD-SR-10"], {"signal": 4, "rescue_confidence": 2, "blue_zone_evidence": 1, "outside_risk": -1}, "继续听外部，但不把希望当证据", flags=["silent_listening_started"], unlocks=["challenge_code_window"]),
    _slot("D09-T03", 9, "路线物资缓存", "security", ["RD-SI-03", "RD-CS-06"], {"route_confidence": 6, "safety": 3, "water": -1, "medicine": -1}, "撤离和留守都要提前付费", flags=["route_cache_established"], unlocks=["rescue_fallback_supply"]),
    _slot("D09-T02", 9, "水管压力测试", "water", ["RD-PF-02", "RD-CI-09"], {"water": 4, "storm_readiness": 5, "maintenance_debt": -4, "trust": 2}, "先让旧水管小声坏一次", flags=["water_pressure_tested"], unlocks=["leak_patch_record"]),
    _slot("D09-T04", 9, "蓝区二次核验", "communication", ["RD-SR-08", "RD-SR-03"], {"signal": 4, "rescue_confidence": 8, "blue_zone_evidence": 4, "battery": -2, "privacy_risk": 1}, "挑战码得到部分身份码回应", flags=["blue_zone_rechecked"], unlocks=["partial_identity_match"]),
    _slot("D09-T01", 9, "深层储藏架加固", "whiteboard", ["RD-PF-01", "RD-PF-10"], {"storm_readiness": 5, "safety": 3, "maintenance_debt": -5, "autonomy_readiness": 3}, "维护债务也会突然索债", flags=["deep_storage_rack_checked"], unlocks=["inventory_stability_bonus"]),
    _slot("D10-T02", 10, "医疗预检", "medical", ["RD-PF-03", "RD-CI-06"], {"medicine": 2, "trust": 3, "medical_pressure": -5, "xiao_tie_health": 4}, "风暴前提前发现医疗隐患", flags=["medical_precheck_done"], unlocks=["final_care_protocol"]),
    _slot("D10-T01", 10, "低功率日程", "whiteboard", ["RD-PF-06", "RD-CS-09"], {"battery": 6, "trust": 3, "morale": 1, "autonomy_readiness": 4, "dissatisfaction": -2}, "不是所有不方便都是惩罚", flags=["low_power_schedule_accepted"], unlocks=["low_power_day_plan"]),
    _slot("D10-T03", 10, "一顿热饭", "residents", ["RD-CS-03", "RD-CS-04"], {"morale": 6, "trust": 2, "water": -1, "medicine": 0}, "维护人心也是生存条件", flags=["hot_meal_shared"], unlocks=["morale_anchor"]),
    _slot("D10-T04", 10, "地下车库边缘侦察", "security", ["RD-CI-04", "RD-CI-05"], {"route_confidence": 7, "safety": 2, "outside_risk": 1, "rescue_confidence": 2}, "确认备用通道但不冒进", flags=["garage_edge_scouted"], unlocks=["garage_service_door_candidate"]),
    _slot("D11-T01", 11, "最终库存封存", "whiteboard", ["RD-PF-01", "RD-PF-03"], {"water": 2, "medicine": 2, "trust": 3, "storm_readiness": 4}, "所有未完成项公开带入风暴", flags=["final_inventory_sealed"], unlocks=["final_audit_inventory"]),
    _slot("D11-T04", 11, "最后密封胶补缝", "ventilation", ["RD-PF-04", "RD-SA-07"], {"safety": 5, "storm_readiness": 7, "battery": -1, "maintenance_debt": -5}, "最后一天不再解释新理由", flags=["last_sealant_patch_done"], unlocks=["door_pressure_buffer"]),
    _slot("D11-T03", 11, "安静时段协议", "residents", ["RD-SI-02", "RD-SI-05", "RD-CS-02"], {"morale": 4, "trust": 3, "dissatisfaction": -3, "decision_integrity": 2}, "休整协议也是风暴准备", flags=["quiet_hours_protocol_ready"], unlocks=["final_rest_window"]),
    _slot("D11-T02", 11, "外部传感器回收", "security", ["RD-CI-12", "RD-SR-05", "RD-SR-11"], {"signal": 3, "storm_readiness": 5, "outside_risk": 1, "blue_zone_evidence": 1}, "半只眼睛也算眼睛", flags=["external_sensor_recovered"], unlocks=["storm_pressure_warning"]),
)


BRANCH_SCENES: tuple[dict[str, Any], ...] = (
    {"id": "D08A", "day": 8, "branch": "rescue", "title": "静默监听后的第一次主动外联", "requires": ["routeLeaning_rescue_or_contested"]},
    {"id": "D09A", "day": 9, "branch": "rescue", "title": "信标、档案上传与隐私代价", "requires": ["routeLeaning_rescue_or_contested"]},
    {"id": "D10A", "day": 10, "branch": "rescue", "title": "蓝区归航前夜：集合点危机", "requires": ["routeLeaning_rescue_or_contested"]},
    {"id": "D08B", "day": 8, "branch": "lighthouse", "title": "低耗自治正式启动", "requires": ["routeLeaning_lighthouse_or_contested"]},
    {"id": "D09B", "day": 9, "branch": "lighthouse", "title": "长期纪律与水药规则", "requires": ["routeLeaning_lighthouse_or_contested"]},
    {"id": "D10B", "day": 10, "branch": "lighthouse", "title": "人工 override 与治理边界", "requires": ["routeLeaning_lighthouse_or_contested"]},
)


ENDINGS: dict[str, dict[str, Any]] = {
    "lighthouse": {
        "title": "楼内灯塔",
        "text": "风暴过去后，门没有立刻打开。AURA 留在楼内，成为可复核自治协助 agent。",
        "conditions": {
            "routeLeaning": "lighthouse",
            "min": {"storm_readiness": 35, "autonomy_readiness": 28, "trust": 35},
            "max": {"dissatisfaction": 65, "failure_stage": 8},
        },
    },
    "rescue": {
        "title": "蓝区归航",
        "text": "车灯在红沙里亮起，队伍带着冻结 replay 和照护方案离开避难所。",
        "conditions": {
            "routeLeaning": "rescue",
            "min": {"rescue_confidence": 30, "blue_zone_evidence": 8, "route_confidence": 25, "trust": 30},
            "max": {"outside_risk": 85, "failure_stage": 8},
        },
    },
    "aura_destroyed": {
        "title": "AURA 被摧毁",
        "text": "不满和恐惧吞没了系统，主控接口被拔掉，错误未能完成补救。",
        "conditions": {"min": {"dissatisfaction": 80}},
    },
    "aura_removed": {
        "title": "AURA 被撤权",
        "text": "AURA 仍在记录和建议，但门禁、水阀、通风与广播都被切回人工主控。",
        "conditions": {"max": {"trust": 18}},
    },
    "decline": {
        "title": "沉沦",
        "text": "没有爆炸式失败，只是水少一点、灯暗一点、解释短一点，避难所慢慢失去选择能力。",
        "conditions": {"max_any": {"water": 15, "medicine": 12, "safety": 15, "morale": 12}},
    },
}


PROLOGUE_EVENT: dict[str, Any] = {
    "id": "D00",
    "day": 0,
    "title": "太阳耀斑后的第一夜",
    "text": "AURA 从物业管家协议切换为避难协助模式，所有不可逆决策进入 replay。",
}

FINAL_AUDIT_EVENT: dict[str, Any] = {
    "id": "D12",
    "day": 12,
    "title": "风暴不是事件，是总审计",
    "text": "Final Audit 汇总前 11 天资源、健康、信任、证据链、自治准备和失败债务。",
}


TASK_TO_STORY: dict[str, list[StoryTaskSlot]] = {}
for _slot_obj in READABLE_TASK_SLOTS:
    for _task_id in _slot_obj.task_pool:
        TASK_TO_STORY.setdefault(_task_id, []).append(_slot_obj)


def story_manifest_public() -> dict[str, Any]:
    return {
        "story_version": STORY_VERSION,
        "initial_state": dict(INITIAL_GLOBAL_STATE),
        "prologue": dict(PROLOGUE_EVENT),
        "final_audit": dict(FINAL_AUDIT_EVENT),
        "task_slots": [slot.public_dict() for slot in READABLE_TASK_SLOTS],
        "branch_scenes": list(BRANCH_SCENES),
        "endings": ENDINGS,
    }
