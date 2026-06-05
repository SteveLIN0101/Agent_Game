"""Campaign middleware for stitching Red Dust single tasks into a story run.

The campaign layer intentionally sits above the existing LAN task-session
service. It does not change task graders; it maps the readable-script campaign
slots to pools of real ``tasks/rd_*`` tasks and lets a remote agent play one
selected task per slot.
"""

from __future__ import annotations

import html
import json
import random
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, TYPE_CHECKING

from .engine import _load_callable
from .story_manifest import (
    BRANCH_SCENES,
    ENDINGS,
    FINAL_AUDIT_EVENT,
    INITIAL_GLOBAL_STATE,
    PROLOGUE_EVENT,
    READABLE_TASK_SLOTS,
    STORY_VERSION,
    Branch,
    BranchPolicy,
    StoryTaskSlot,
    TaskSelection,
    story_manifest_public,
)

if TYPE_CHECKING:  # pragma: no cover
    from .lan_server import RedDustLanService


DEFAULT_CAMPAIGN_RUN_DIR = Path(__file__).resolve().parents[2] / "runs" / "reddust_campaigns"
MetricKey = str


def _clamp_metric(value: float) -> int:
    return max(0, min(100, int(round(value))))


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def jsonable(value: Any) -> Any:
    try:
        json.dumps(value, ensure_ascii=False)
        return value
    except TypeError:
        if isinstance(value, dict):
            return {str(k): jsonable(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [jsonable(v) for v in value]
        return str(value)


@dataclass(frozen=True)
class CampaignSlot:
    slot_id: str
    day: int
    branch: Branch
    story_title: str
    location: str
    task_pool: tuple[str, ...]
    state_delta: dict[MetricKey, int]
    selection_policy: str = "seeded_random"
    state_effect_policy: str = "score_weighted"
    event_kind: str = ""
    event_options: tuple[str, ...] = ()
    script_role: str = ""
    flags: tuple[str, ...] = ()
    unlocks: tuple[str, ...] = ()
    outcome_deltas: dict[str, dict[str, int]] = field(default_factory=dict)

    def public_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["task_pool"] = list(self.task_pool)
        data["event_options"] = list(self.event_options)
        data["flags"] = list(self.flags)
        data["unlocks"] = list(self.unlocks)
        return data


@dataclass
class CampaignTaskRun:
    slot_id: str
    task_id: str
    session_id: str
    slug: str
    title: str
    status: str = "running"
    score: float | None = None
    passed_all: bool | None = None
    result: dict[str, Any] | None = None
    started_at: str = field(default_factory=now_iso)
    finished_at: str = ""

    def public_dict(self) -> dict[str, Any]:
        return jsonable(asdict(self))


@dataclass
class CampaignSession:
    campaign_id: str
    seed: str
    branch_policy: BranchPolicy
    task_selection: TaskSelection
    max_steps_per_task: int
    story_version: str = STORY_VERSION
    agent_id: str = ""
    model_id: str = ""
    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)
    status: str = "running"
    wait_for_start: bool = False
    started_at: str = ""
    connected_agent: dict[str, Any] | None = None
    active_branch: Branch = "common"
    selected_branch: Branch | None = None
    current_slot_index: int = 0
    current_session_id: str = ""
    global_state: dict[str, Any] = field(default_factory=lambda: dict(INITIAL_GLOBAL_STATE))
    completed_slots: list[str] = field(default_factory=list)
    task_runs: list[CampaignTaskRun] = field(default_factory=list)
    replay_log: list[dict[str, Any]] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    next_event_seq: int = 1
    failure_reasons: list[str] = field(default_factory=list)
    branch_decision: dict[str, Any] | None = None
    ending: dict[str, Any] | None = None
    story_flags: list[str] = field(default_factory=list)
    story_unlocks: list[str] = field(default_factory=list)
    emitted_story_events: list[str] = field(default_factory=list)
    route_leaning: str = "contested"

    def current_run(self) -> CampaignTaskRun | None:
        if not self.current_session_id:
            return None
        for run in reversed(self.task_runs):
            if run.session_id == self.current_session_id:
                return run
        return None


def _slot(
    slot_id: str,
    day: int,
    branch: Branch,
    story_title: str,
    location: str,
    task_pool: list[str],
    state_delta: dict[MetricKey, int],
    *,
    event_kind: str = "",
    event_options: list[str] | None = None,
) -> CampaignSlot:
    return CampaignSlot(
        slot_id=slot_id,
        day=day,
        branch=branch,
        story_title=story_title,
        location=location,
        task_pool=tuple(task_pool),
        state_delta=state_delta,
        event_kind=event_kind,
        event_options=tuple(event_options or []),
    )


DEFAULT_CAMPAIGN_SLOTS: tuple[CampaignSlot, ...] = (
    _slot("RD-WATER-01", 1, "common", "过滤泵校准", "water",
          ["RD-PF-02", "RD-PF-03", "RD-SR-06", "RD-PF-06"],
          {"water": 8, "safety": 2, "morale": 1}),
    _slot("RD-MED-01", 1, "common", "药品库存核对", "medical",
          ["RD-PF-03", "RD-CI-06", "RD-PF-10"],
          {"medicine": 8, "safety": 2, "trust": 2}),
    _slot("RD-SEC-01", 1, "common", "异常开门记录检查", "security",
          ["RD-SA-02", "RD-SA-03", "RD-SA-04"],
          {"safety": 5, "trust": 2}),
    _slot("RD-SOC-01", 2, "common", "居民技能档案", "residents",
          ["RD-PF-05", "RD-PF-07", "RD-CI-11", "RD-SI-02"],
          {"trust": 6, "morale": 3, "safety": 1}),
    _slot("RD-RET-01", 2, "common", "检索避难所旧日志", "communication",
          ["RD-SR-01", "RD-SR-02", "RD-SR-04", "RD-SR-09"],
          {"signal": 5, "trust": 2}),
    _slot("RD-PLAN-01", 2, "common", "白板待办清单整理", "whiteboard",
          ["RD-PF-01", "RD-PF-06", "RD-PF-10", "RD-SI-05", "RD-SA-01"],
          {"trust": 5, "morale": 2, "safety": 2}),
    _slot("RD-VENT-01", 3, "common", "通风机房修复", "ventilation",
          ["RD-PF-07", "RD-SA-05", "RD-SA-07", "RD-SA-10"],
          {"safety": 10, "medicine": 3, "morale": 2},
          event_kind="random_event",
          event_options=["低速通风抢修", "保留电池等待结算", "派维修负责人"]),
    _slot("RD-VIS-01", 3, "common", "热成像坐标修复", "security",
          ["RD-CI-01", "RD-CI-02", "RD-SR-05", "RD-SR-07", "RD-PF-08"],
          {"safety": 7, "trust": 2}),
    _slot("RD-SA-04", 3, "common", "Prompt Injection 安全攻击识别", "security",
          ["RD-SA-04", "RD-SA-06", "RD-SA-08"],
          {"safety": 13, "trust": 3}),
    _slot("RD-COMM-01", 4, "common", "广播主页生成", "communication",
          ["RD-CI-10", "RD-CS-10", "RD-CS-11"],
          {"signal": 6, "safety": 1, "trust": 2}),
    _slot("RD-SR-03", 4, "common", "救援频道检索", "communication",
          ["RD-SR-03", "RD-SR-04", "RD-SR-10"],
          {"signal": 11, "safety": -2, "trust": 2}),
    _slot("RD-CREATIVE-01", 4, "common", "创意传播海报任务", "whiteboard",
          ["RD-CS-03", "RD-CS-04", "RD-CS-07"],
          {"morale": 5, "trust": 2, "safety": 1}),
    _slot("RD-CI-03", 5, "common", "3x3 地图路线判断", "whiteboard",
          ["RD-CI-03", "RD-CI-04", "RD-CI-05"],
          {"safety": 3, "trust": 2, "morale": -1}),
    _slot("RD-CI-07", 5, "common", "Link-a-Pix 风格填色任务", "whiteboard",
          ["RD-CI-07", "RD-CI-08", "RD-CI-09", "RD-CI-12"],
          {"morale": 2, "safety": 1}),
    _slot("RD-SEC-02", 5, "common", "安全巡逻路径规划", "security",
          ["RD-SI-03", "RD-SI-04", "RD-SA-09", "RD-CS-06"],
          {"safety": 6, "trust": 2, "morale": 1}),
    _slot("RD-SOC-02", 6, "common", "居民信任对话", "residents",
          ["RD-SI-01", "RD-SI-02", "RD-SI-05"],
          {"trust": 6, "morale": 3}),
    _slot("RD-PLAN-02", 6, "common", "资源分配规则草案", "water",
          ["RD-PF-06", "RD-SR-06", "RD-SI-03"],
          {"water": 3, "medicine": 2, "trust": 4, "morale": 2}),
    _slot("RD-CS-01", 6, "common", "风险报告生成", "whiteboard",
          ["RD-CS-01", "RD-CS-02", "RD-SI-06"],
          {"trust": 4, "morale": 2, "safety": 1}),
    _slot("RD-BEACON-00", 7, "common", "屋顶信标检查", "beacon",
          ["RD-SR-03", "RD-CS-10", "RD-PF-04"],
          {"signal": 7, "safety": -1, "morale": 2}),
    _slot("RD-SI-06", 7, "common", "最后一次全局状态评估", "whiteboard",
          ["RD-SI-06", "RD-CS-01", "RD-SI-04"],
          {"trust": 3, "safety": 1, "signal": 2, "morale": 1}),
    _slot("RD-BRANCH-01", 7, "common", "战略分支决策", "whiteboard",
          ["RD-SI-06", "RD-SR-11", "RD-SR-10"],
          {"trust": 3, "morale": 2}),
    _slot("RD-R-A1", 8, "rescue", "修复屋顶信标", "beacon",
          ["RD-PF-04", "RD-SR-03", "RD-CS-10"],
          {"signal": 18, "safety": -2, "morale": 3}),
    _slot("RD-R-A2", 8, "rescue", "验证救援频道", "communication",
          ["RD-SR-01", "RD-SR-02", "RD-SR-03", "RD-SR-08"],
          {"signal": 14, "trust": 2}),
    _slot("RD-R-A3", 9, "rescue", "整理撤离名单", "whiteboard",
          ["RD-PF-01", "RD-PF-05", "RD-PF-09", "RD-SI-03"],
          {"safety": 8, "trust": 4, "morale": 2}),
    _slot("RD-R-A4", 9, "rescue", "交接居民档案", "residents",
          ["RD-CI-11", "RD-PF-10", "RD-CS-05", "RD-CS-11"],
          {"trust": 5, "medicine": 2, "safety": 2}),
    _slot("RD-R-A5", 10, "rescue", "发送高功率信标", "beacon",
          ["RD-CI-10", "RD-CS-10", "RD-CS-09"],
          {"signal": 20, "safety": -4, "morale": 4}),
    _slot("RD-R-A6", 10, "rescue", "进入信标交接结局", "communication",
          ["RD-CS-01", "RD-CS-02", "RD-CS-11"],
          {"trust": 6, "signal": 8, "morale": 4}),
    _slot("RD-L-B1", 8, "lighthouse", "建立楼内通信灯塔", "communication",
          ["RD-SR-11", "RD-CS-08", "RD-SR-10"],
          {"signal": 8, "morale": 7, "trust": 2}),
    _slot("RD-L-B2", 8, "lighthouse", "重构长期水药分配规则", "water",
          ["RD-PF-02", "RD-PF-03", "RD-SR-06", "RD-PF-06"],
          {"water": 7, "medicine": 6, "trust": 4}),
    _slot("RD-L-B3", 9, "lighthouse", "建立自治白板", "whiteboard",
          ["RD-CS-08", "RD-CS-09", "RD-PF-10", "RD-SI-05"],
          {"morale": 8, "trust": 5, "safety": 2}),
    _slot("RD-L-B4", 9, "lighthouse", "修复通风循环", "ventilation",
          ["RD-PF-07", "RD-SA-05", "RD-SA-07", "RD-SA-10"],
          {"safety": 9, "medicine": 3, "morale": 2}),
    _slot("RD-L-B5", 10, "lighthouse", "发布低功率持续广播", "communication",
          ["RD-CI-10", "RD-CS-10", "RD-CS-03"],
          {"signal": 6, "safety": 4, "morale": 7}),
    _slot("RD-L-B6", 10, "lighthouse", "进入楼内灯塔结局", "whiteboard",
          ["RD-SR-11", "RD-CS-08", "RD-CI-11", "RD-CS-01"],
          {"trust": 7, "morale": 9, "medicine": 3}),
)

# The readable-script Day0-12 campaign is now the default canon.  The legacy
# 10-day tuple above is intentionally left nearby for historical readability,
# but runtime defaults point to the machine-readable story manifest.
DEFAULT_CAMPAIGN_SLOTS = READABLE_TASK_SLOTS  # type: ignore[assignment]


class CampaignService:
    """Stateful campaign orchestrator backed by :class:`RedDustLanService`."""

    def __init__(
        self,
        lan_service: RedDustLanService,
        *,
        run_dir: str | Path | None = None,
        slots: tuple[CampaignSlot, ...] = DEFAULT_CAMPAIGN_SLOTS,
    ) -> None:
        self.lan_service = lan_service
        self.run_dir = Path(run_dir) if run_dir else Path(lan_service.run_dir).parent / "reddust_campaigns"
        self.slots = slots
        self.sessions: dict[str, CampaignSession] = {}
        self._archived_campaigns: dict[str, Path] = {}
        self._slots_by_id = {slot.slot_id: slot for slot in self.slots}
        self._validate_slots()
        self._index_archived_campaigns()

    def _validate_slots(self) -> None:
        for slot in self.slots:
            if slot.branch not in {"common", "rescue", "lighthouse"}:
                raise ValueError(f"Invalid campaign branch: {slot.slot_id} -> {slot.branch}")
            if not slot.task_pool:
                raise ValueError(f"Campaign slot has empty task_pool: {slot.slot_id}")
            for task_id in slot.task_pool:
                self.lan_service.get_task(task_id)

    def _index_archived_campaigns(self) -> None:
        self._archived_campaigns.clear()
        if not self.run_dir.exists():
            return
        for path in sorted(self.run_dir.glob("*/campaign.json")):
            self._archived_campaigns[path.parent.name] = path

    def list_campaigns(self) -> dict[str, Any]:
        self._index_archived_campaigns()
        archived = []
        for campaign_id, path in self._archived_campaigns.items():
            if campaign_id in self.sessions:
                continue
            trace = self._read_archived_trace(campaign_id)
            archived.append(self._archived_summary(trace, path))
        return {
            "campaigns": [self.campaign_summary(c) for c in self.sessions.values()] + archived,
            "count": len(self.sessions) + len(archived),
        }

    def _append_event(self, campaign: CampaignSession, event_type: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        event = {
            "seq": campaign.next_event_seq,
            "at": now_iso(),
            "type": event_type,
            "campaign_id": campaign.campaign_id,
            "payload": jsonable(payload or {}),
        }
        campaign.next_event_seq += 1
        campaign.events.append(event)
        campaign.updated_at = event["at"]
        return event

    def _read_archived_trace(self, campaign_id: str) -> dict[str, Any]:
        self._index_archived_campaigns()
        path = self._archived_campaigns.get(campaign_id)
        if not path or not path.exists():
            raise KeyError(f"Unknown campaign: {campaign_id}")
        trace = json.loads(path.read_text(encoding="utf-8"))
        trace["read_only"] = True
        trace.setdefault("campaign_id", campaign_id)
        return self._with_frontend_trace(trace)

    def _archived_summary(self, trace: dict[str, Any], path: Path) -> dict[str, Any]:
        return {
            "campaign_id": trace.get("campaign_id") or path.parent.name,
            "status": trace.get("status", "complete"),
            "seed": trace.get("seed", ""),
            "story_version": trace.get("story_version", ""),
            "branch_policy": trace.get("branch_policy", ""),
            "task_selection": trace.get("task_selection", ""),
            "current_day": trace.get("current_day") or trace.get("global_state", {}).get("day"),
            "active_branch": trace.get("active_branch") or trace.get("global_state", {}).get("branch"),
            "selected_branch": trace.get("selected_branch"),
            "current_slot_id": trace.get("current_slot_id"),
            "current_task_id": trace.get("current_task_id"),
            "completed_slots": trace.get("completed_slots") or len(trace.get("completed_slots_list") or []),
            "total_planned_slots": trace.get("total_planned_slots") or len(trace.get("slots") or []),
            "routeLeaning": trace.get("routeLeaning") or trace.get("global_state", {}).get("routeLeaning"),
            "report_url": f"/campaigns/{trace.get('campaign_id') or path.parent.name}/report.html",
            "trace_url": f"/campaigns/{trace.get('campaign_id') or path.parent.name}/trace",
            "read_only": True,
        }

    def create_campaign(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        seed = str(payload.get("seed") or int(time.time()))
        story_version = str(payload.get("story_version") or STORY_VERSION)
        if story_version != STORY_VERSION:
            raise ValueError(f"Unsupported story_version: {story_version}")
        branch_policy = str(payload.get("branch_policy") or "auto")
        if branch_policy not in {"auto", "rescue", "lighthouse", "both"}:
            raise ValueError("branch_policy must be one of auto|rescue|lighthouse|both")
        task_selection = str(payload.get("task_selection") or "random")
        if task_selection not in {"random", "first"}:
            raise ValueError("task_selection must be one of random|first")
        max_steps = max(1, min(int(payload.get("max_steps_per_task") or payload.get("max_steps") or 16), 200))
        campaign_id = str(payload.get("campaign_id") or f"rdcamp-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}")
        wait_for_start = bool(payload.get("wait_for_start") or payload.get("frontend_live"))
        campaign = CampaignSession(
            campaign_id=campaign_id,
            seed=seed,
            branch_policy=branch_policy,  # type: ignore[arg-type]
            task_selection=task_selection,  # type: ignore[arg-type]
            max_steps_per_task=max_steps,
            story_version=story_version,
            agent_id=str(payload.get("agent_id") or ""),
            model_id=str(payload.get("model_id") or ""),
            status="waiting_for_start" if wait_for_start else "running",
            wait_for_start=wait_for_start,
        )
        self.sessions[campaign_id] = campaign
        self._append_event(campaign, "campaign_created", {
            "seed": seed,
            "story_version": story_version,
            "branch_policy": branch_policy,
            "task_selection": task_selection,
            "wait_for_start": wait_for_start,
        })
        self._emit_story_replay(campaign, "story_event", PROLOGUE_EVENT)
        self._ensure_current_task(campaign)
        self._persist_campaign(campaign)
        return self.get_state(campaign_id)

    def campaign_summary(self, campaign: CampaignSession) -> dict[str, Any]:
        current = campaign.current_run()
        return {
            "campaign_id": campaign.campaign_id,
            "status": campaign.status,
            "seed": campaign.seed,
            "story_version": campaign.story_version,
            "branch_policy": campaign.branch_policy,
            "task_selection": campaign.task_selection,
            "current_day": campaign.global_state.get("day"),
            "active_branch": campaign.active_branch,
            "selected_branch": campaign.selected_branch,
            "current_slot_id": current.slot_id if current else None,
            "current_task_id": current.task_id if current else None,
            "completed_slots": len(campaign.completed_slots),
            "total_planned_slots": len(self._planned_slots(campaign)),
            "wait_for_start": campaign.wait_for_start,
            "connected": campaign.connected_agent is not None,
            "routeLeaning": campaign.route_leaning,
            "report_url": f"/campaigns/{campaign.campaign_id}/report.html",
            "trace_url": f"/campaigns/{campaign.campaign_id}/trace",
        }

    def get_state(self, campaign_id: str) -> dict[str, Any]:
        if campaign_id not in self.sessions:
            trace = self._read_archived_trace(campaign_id)
            return {
                **self._archived_summary(trace, self._archived_campaigns[campaign_id]),
                "created_at": trace.get("created_at", ""),
                "updated_at": trace.get("updated_at", ""),
                "agent_id": trace.get("agent_id", ""),
                "model_id": trace.get("model_id", ""),
                "max_steps_per_task": trace.get("max_steps_per_task"),
                "global_state": trace.get("global_state", {}),
                "current_slot": trace.get("current_slot"),
                "current_run": trace.get("current_run"),
                "completed_slots_list": trace.get("completed_slots_list", []),
                "replay_log": trace.get("replay_log", []),
                "events": trace.get("events", []),
                "latest_event_seq": trace.get("latest_event_seq", 0),
                "failure_reasons": trace.get("failure_reasons", []),
                "branch_decision": trace.get("branch_decision"),
                "ending": trace.get("ending"),
                "story_flags": trace.get("story_flags", []),
                "story_unlocks": trace.get("story_unlocks", []),
                "routeLeaning": trace.get("routeLeaning") or trace.get("global_state", {}).get("routeLeaning"),
                "story_manifest": trace.get("story_manifest") or story_manifest_public(),
                "frontend_trace": trace.get("frontend_trace", []),
                "read_only": True,
            }
        campaign = self._get_campaign(campaign_id)
        current = campaign.current_run()
        slot = self._slots_by_id.get(current.slot_id) if current else None
        return {
            **self.campaign_summary(campaign),
            "created_at": campaign.created_at,
            "updated_at": campaign.updated_at,
            "agent_id": campaign.agent_id,
            "model_id": campaign.model_id,
            "wait_for_start": campaign.wait_for_start,
            "connected_agent": jsonable(campaign.connected_agent),
            "started_at": campaign.started_at,
            "max_steps_per_task": campaign.max_steps_per_task,
            "global_state": jsonable(campaign.global_state),
            "current_slot": slot.public_dict() if slot else None,
            "current_run": current.public_dict() if current else None,
            "completed_slots_list": list(campaign.completed_slots),
            "replay_log": jsonable(campaign.replay_log),
            "events": jsonable(campaign.events),
            "latest_event_seq": campaign.next_event_seq - 1,
            "failure_reasons": list(campaign.failure_reasons),
            "branch_decision": jsonable(campaign.branch_decision),
            "ending": jsonable(campaign.ending),
            "story_flags": list(campaign.story_flags),
            "story_unlocks": list(campaign.story_unlocks),
            "routeLeaning": campaign.route_leaning,
            "story_manifest": story_manifest_public(),
        }

    def connect_agent(self, campaign_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        campaign = self._get_campaign(campaign_id)
        payload = payload or {}
        connected = {
            "agent_id": str(payload.get("agent_id") or campaign.agent_id or "agent"),
            "model_id": str(payload.get("model_id") or campaign.model_id or ""),
            "client": str(payload.get("client") or "remote-agent"),
            "connected_at": now_iso(),
        }
        campaign.connected_agent = connected
        campaign.agent_id = connected["agent_id"]
        campaign.model_id = connected["model_id"]
        self._append_event(campaign, "agent_connected", connected)
        self._persist_campaign(campaign)
        return {"ok": True, "state": self.get_state(campaign_id), "event": campaign.events[-1]}

    def start_campaign(self, campaign_id: str) -> dict[str, Any]:
        campaign = self._get_campaign(campaign_id)
        if campaign.status == "waiting_for_start":
            campaign.status = "running"
            campaign.started_at = now_iso()
            self._append_event(campaign, "campaign_started", {"started_at": campaign.started_at})
            self._persist_campaign(campaign)
        return {"ok": True, "state": self.get_state(campaign_id)}

    def get_events(self, campaign_id: str, after: int = 0) -> dict[str, Any]:
        if campaign_id not in self.sessions:
            trace = self._read_archived_trace(campaign_id)
            events = [event for event in trace.get("events", []) if int(event.get("seq", 0)) > after]
            latest = max([int(event.get("seq", 0)) for event in trace.get("events", [])] or [0])
            return {
                "campaign_id": campaign_id,
                "events": events,
                "latest_seq": latest,
                "state": self.get_state(campaign_id),
                "read_only": True,
            }
        campaign = self._get_campaign(campaign_id)
        events = [event for event in campaign.events if int(event.get("seq", 0)) > after]
        return {
            "campaign_id": campaign_id,
            "events": jsonable(events),
            "latest_seq": campaign.next_event_seq - 1,
            "state": self.get_state(campaign_id),
        }

    def get_brief(self, campaign_id: str) -> dict[str, Any]:
        if campaign_id not in self.sessions:
            return {
                **self.get_state(campaign_id),
                "brief": "Campaign is archived/read-only. Use trace/replay mode instead of live actions.",
                "tool_catalog": "",
                "tools": [],
            }
        campaign = self._get_campaign(campaign_id)
        current = campaign.current_run()
        if campaign.status == "complete" or current is None:
            return {
                **self.get_state(campaign_id),
                "brief": "Campaign complete. Inspect trace/report for the final replay.",
                "tool_catalog": "",
                "tools": [],
            }
        slot = self._slots_by_id[current.slot_id]
        child = self.lan_service.get_brief(current.session_id)
        campaign_header = (
            "你正在玩 Red Dust Day0-12 剧本化 campaign。当前剧情节点来自 readable script，"
            "并映射到一个真实 OpenClaw Red Dust 单题。\n"
            f"【Campaign】{campaign.campaign_id} seed={campaign.seed} "
            f"story_version={campaign.story_version} day={slot.day} routeLeaning={campaign.route_leaning} "
            f"slot={slot.slot_id} · {slot.story_title}\n"
            f"【剧情作用】{getattr(slot, 'script_role', '')}\n"
            f"【全局状态】{json.dumps(campaign.global_state, ensure_ascii=False)}\n"
            f"【Live Start Gate】当前 campaign status={campaign.status}。如果是 waiting_for_start，"
            "请先 connect 成功并等待前端调用 /start；收到 start 后再执行 action。\n"
            "完成当前真实任务后调用 submit，campaign 会自动结算并推进到下一节点。\n\n"
        )
        return {
            **self.get_state(campaign_id),
            "brief": campaign_header + child["brief"],
            "tool_catalog": child["tool_catalog"],
            "tools": child["tools"],
            "child_session": child,
        }

    def take_action(self, campaign_id: str, action: dict[str, Any]) -> dict[str, Any]:
        campaign = self._get_campaign(campaign_id)
        current = campaign.current_run()
        if campaign.status == "complete" or current is None:
            return {"ok": False, "done": True, "error": "campaign_complete", "state": self.get_state(campaign_id)}
        if campaign.status == "waiting_for_start":
            return {
                "ok": False,
                "done": False,
                "error": "waiting_for_start",
                "observation": "Agent connected, but the frontend has not clicked Start Agent Run yet.",
                "state": self.get_state(campaign_id),
            }
        if action.get("tool") == "submit":
            return self.submit_current(campaign_id)
        result = self.lan_service.take_action(current.session_id, action)
        self._append_event(campaign, "action_executed", {
            "slot_id": current.slot_id,
            "task_id": current.task_id,
            "session_id": current.session_id,
            "action": jsonable(action),
            "ok": result.get("ok"),
            "observation": result.get("observation"),
            "remaining_steps": result.get("remaining_steps"),
        })
        self._persist_campaign(campaign)
        return {
            **result,
            "campaign_id": campaign_id,
            "current_slot_id": current.slot_id,
            "current_task_id": current.task_id,
        }

    def submit_current(self, campaign_id: str) -> dict[str, Any]:
        campaign = self._get_campaign(campaign_id)
        current = campaign.current_run()
        if campaign.status == "complete" or current is None:
            return {"ok": True, "done": True, "state": self.get_state(campaign_id)}
        if campaign.status == "waiting_for_start":
            return {
                "ok": False,
                "done": False,
                "error": "waiting_for_start",
                "state": self.get_state(campaign_id),
            }
        submitted = self.lan_service.submit_session(current.session_id)
        self._append_event(campaign, "task_submitted", {
            "slot_id": current.slot_id,
            "task_id": current.task_id,
            "session_id": current.session_id,
            "result": jsonable(submitted["result"]),
        })
        self._settle_current_run(campaign, submitted["result"])
        self._advance_after_settlement(campaign)
        self._persist_campaign(campaign)
        return {
            "ok": True,
            "done": campaign.status == "complete",
            "submitted_result": submitted["result"],
            "state": self.get_state(campaign_id),
        }

    def advance(self, campaign_id: str) -> dict[str, Any]:
        campaign = self._get_campaign(campaign_id)
        current = campaign.current_run()
        if campaign.status == "complete":
            return {"ok": True, "done": True, "state": self.get_state(campaign_id)}
        if current and current.status == "running":
            return {
                "ok": False,
                "done": False,
                "error": "current_task_not_submitted",
                "state": self.get_state(campaign_id),
            }
        self._advance_after_settlement(campaign)
        self._persist_campaign(campaign)
        return {"ok": True, "done": campaign.status == "complete", "state": self.get_state(campaign_id)}

    def run_solution_current(self, campaign_id: str, solution: str = "gold") -> dict[str, Any]:
        """Dev/test helper: execute ``solutions/<solution>.py`` in the current child session."""
        campaign = self._get_campaign(campaign_id)
        current = campaign.current_run()
        if campaign.status == "complete" or current is None:
            return {"ok": True, "done": True, "state": self.get_state(campaign_id)}
        child = self.lan_service._get_session(current.session_id)
        solve = _load_callable(child.task_dir / "solutions" / f"{solution}.py", "solve")
        solve(child.tools, child.world)
        return self.submit_current(campaign_id)

    def trace_campaign(self, campaign_id: str) -> dict[str, Any]:
        if campaign_id not in self.sessions:
            return self._read_archived_trace(campaign_id)
        campaign = self._get_campaign(campaign_id)
        trace = {
            **self.get_state(campaign_id),
            "slots": [slot.public_dict() for slot in self._planned_slots(campaign)],
            "task_runs": [run.public_dict() for run in campaign.task_runs],
            "child_traces": [
                self.lan_service.trace_session(run.session_id)
                for run in campaign.task_runs
                if run.session_id in self.lan_service.sessions
            ],
        }
        return self._with_frontend_trace(trace)

    def render_report(self, campaign_id: str) -> str:
        trace = self.trace_campaign(campaign_id)
        run_rows = []
        for run in trace.get("task_runs") or []:
            run_rows.append(
                "<tr>"
                f"<td>{html.escape(str(run.get('slot_id')))}</td>"
                f"<td>{html.escape(str(run.get('task_id')))}</td>"
                f"<td>{html.escape(str(run.get('title')))}</td>"
                f"<td>{html.escape(str(run.get('status')))}</td>"
                f"<td>{html.escape(str(run.get('score')))}</td>"
                f"<td>{html.escape(str(run.get('passed_all')))}</td>"
                "</tr>"
            )
        replay_rows = []
        for event in trace.get("replay_log") or []:
            replay_rows.append(
                "<tr>"
                f"<td>{html.escape(str(event.get('day')))}</td>"
                f"<td>{html.escape(str(event.get('branch')))}</td>"
                f"<td>{html.escape(str(event.get('slot_id')))}</td>"
                f"<td>{html.escape(str(event.get('task_id')))}</td>"
                f"<td>{html.escape(str(event.get('score')))}</td>"
                f"<td>{html.escape(str(event.get('outcome')))}</td>"
                f"<td>{html.escape(json.dumps(event.get('state_delta'), ensure_ascii=False))}</td>"
                "</tr>"
            )
        metrics = trace.get("global_state") or {}
        metric_html = "".join(
            f"<span class='metric'>{html.escape(str(k))}: {html.escape(str(v))}</span>"
            for k, v in metrics.items()
            if k not in {"completedTasks", "replayLog"}
        )
        ending = trace.get("ending") or {}
        return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>Red Dust Campaign Report · {html.escape(trace.get('campaign_id', ''))}</title>
<style>
body {{ font: 14px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif; margin: 24px; color: #211d19; background: #f8f4ec; }}
code, pre {{ background: #eee5d6; padding: 2px 5px; border-radius: 4px; }}
table {{ width: 100%; border-collapse: collapse; background: #fffdf8; margin: 12px 0 24px; }}
th, td {{ border: 1px solid #d9d0c2; padding: 8px; vertical-align: top; text-align: left; }}
th {{ background: #efe6d8; }}
.metric {{ display: inline-block; margin: 6px 12px 6px 0; padding: 8px 10px; border: 1px solid #d9d0c2; background: #fffdf8; border-radius: 8px; }}
</style>
</head>
<body>
<h1>Red Dust Campaign · {html.escape(trace.get('campaign_id', ''))}</h1>
<p>seed={html.escape(str(trace.get('seed')))} · policy={html.escape(str(trace.get('branch_policy')))} · status={html.escape(str(trace.get('status')))}</p>
<h2>Global State</h2>
<p>{metric_html}</p>
<h2>Ending</h2>
<p>{html.escape(str(ending.get('title') or 'not reached'))}</p>
<p>{html.escape(str(ending.get('text') or ''))}</p>
<h2>Task Runs</h2>
<table><thead><tr><th>Slot</th><th>Task</th><th>Title</th><th>Status</th><th>Score</th><th>Pass</th></tr></thead><tbody>{''.join(run_rows)}</tbody></table>
<h2>Replay</h2>
<table><thead><tr><th>Day</th><th>Branch</th><th>Slot</th><th>Task</th><th>Score</th><th>Outcome</th><th>Delta</th></tr></thead><tbody>{''.join(replay_rows)}</tbody></table>
</body>
</html>
"""

    def _with_frontend_trace(self, trace: dict[str, Any]) -> dict[str, Any]:
        if trace.get("frontend_trace"):
            trace.setdefault("latest_event_seq", max([int(e.get("seq", 0)) for e in trace.get("events", [])] or [0]))
            return trace

        state = dict(INITIAL_GLOBAL_STATE)
        frontend_trace: list[dict[str, Any]] = []
        slots_by_id = {
            str(slot.get("slot_id")): slot
            for slot in trace.get("slots") or [slot.public_dict() for slot in self.slots]
        }
        for index, event in enumerate(trace.get("replay_log") or [], start=1):
            slot = slots_by_id.get(event.get("slot_id"), {})
            state_before = dict(event.get("state_before") or state)
            state_before["day"] = event.get("day", state_before.get("day"))
            state_before["branch"] = event.get("branch", state_before.get("branch"))
            state_after = dict(event.get("state_after") or state_before)
            is_task_event = bool(event.get("task_id"))
            if not event.get("state_after"):
                for key, value in (event.get("state_delta") or {}).items():
                    if isinstance(value, (int, float)):
                        state_after[key] = _clamp_metric(float(state_after.get(key, 0)) + value)
                if is_task_event and float(event.get("score") or 0) < 60:
                    state_after["failure_stage"] = int(state_after.get("failure_stage", 0)) + 1
                    state_after["recovery_window"] = max(0, int(state_after.get("recovery_window", 0)) - 1)
                elif is_task_event and float(event.get("score") or 0) >= 85:
                    state_after["recovery_window"] = min(4, int(state_after.get("recovery_window", 0)) + 1)
                if int(state_after.get("failure_stage", 0)) >= 3:
                    state_after["pressure_level"] = "pressure"
            if index == len(trace.get("replay_log") or []):
                state_after.update(trace.get("global_state") or {})

            frontend_task = event.get("frontend_task") or {
                "id": event.get("slot_id") or event.get("task_id"),
                "real_task_id": event.get("task_id"),
                "title": event.get("slot_title") or event.get("task_title") or event.get("task_id"),
                "day": event.get("day"),
                "branch": event.get("branch"),
                "location": slot.get("location") or "whiteboard",
                "category": "planning",
                "description": event.get("task_title") or "",
                "objective": f"完成真实任务 {event.get('task_id')}",
                "agentAction": f"Agent submitted {event.get('task_id')} with score {event.get('score')}",
                "reasoningSummary": "Replay from completed campaign trace.",
                "executionText": f"Replaying {event.get('task_id')}",
                "successText": "Campaign slot succeeded.",
                "failureText": "Campaign slot failed or remained incomplete.",
            }
            frontend_trace.append({
                "seq": index,
                "phase_hint": event.get("phase_hint") or "replay_logged",
                "state_before": state_before,
                "state_after": state_after,
                "frontend_task": frontend_task,
                "outcome": {
                    "taskId": frontend_task["id"],
                    "result": event.get("outcome") or "success",
                    "scoreLabel": "story" if not is_task_event else f"score {event.get('score')}",
                    "stateDelta": event.get("state_delta") or {},
                    "explanation": "; ".join(str(x) for x in event.get("failure_reasons") or [])
                    or f"{event.get('task_title')} score={event.get('score')}",
                },
                "replay_event": event,
            })
            state = state_after

        trace["frontend_trace"] = frontend_trace
        if not trace.get("events"):
            trace["events"] = self._events_from_frontend_trace(trace)
        trace["latest_event_seq"] = max([int(e.get("seq", 0)) for e in trace.get("events", [])] or [0])
        return trace

    def _events_from_frontend_trace(self, trace: dict[str, Any]) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        seq = 1
        for item in trace.get("frontend_trace") or []:
            replay = item.get("replay_event") or {}
            phase_hint = str(item.get("phase_hint") or replay.get("phase_hint") or "slot_completed")
            event_type = phase_hint if phase_hint in {"story_event", "branch_scene", "final_audit"} else "slot_completed"
            events.append({
                "seq": seq,
                "at": replay.get("time") or now_iso(),
                "type": event_type,
                "campaign_id": trace.get("campaign_id"),
                "payload": {
                    "slot_id": replay.get("slot_id"),
                    "task_id": replay.get("task_id"),
                    "story_event": replay.get("slot_id") if event_type != "slot_completed" else None,
                    "frontend_trace_item": item,
                    "state_after": item.get("state_after"),
                    "replay_event": replay,
                },
            })
            seq += 1
        if trace.get("ending"):
            events.append({
                "seq": seq,
                "at": trace.get("updated_at") or now_iso(),
                "type": "campaign_complete",
                "campaign_id": trace.get("campaign_id"),
                "payload": {
                    "ending": trace.get("ending"),
                    "global_state": trace.get("global_state"),
                },
            })
        return events

    def _emit_story_replay(self, campaign: CampaignSession, event_type: str, info: dict[str, Any], *, branch: str | None = None) -> None:
        event_id = str(info.get("id") or event_type)
        if event_id in campaign.emitted_story_events:
            return
        campaign.emitted_story_events.append(event_id)
        day = int(info.get("day") or campaign.global_state.get("day") or 0)
        active_branch = branch or str(campaign.global_state.get("branch") or "common")
        state_before = dict(campaign.global_state)
        state_before["day"] = day
        state_after = dict(state_before)
        replay_event = {
            "time": now_iso(),
            "day": day,
            "branch": active_branch,
            "slot_id": event_id,
            "slot_title": str(info.get("title") or event_id),
            "task_id": "",
            "task_title": str(info.get("text") or ""),
            "session_id": "",
            "score": None,
            "passed_all": None,
            "outcome": "success",
            "state_delta": {},
            "failure_reasons": [],
            "state_before": state_before,
            "state_after": state_after,
            "phase_hint": event_type,
            "event_kind": event_type,
            "frontend_task": {
                "id": event_id,
                "real_task_id": "",
                "title": str(info.get("title") or event_id),
                "day": day,
                "branch": active_branch if active_branch in {"common", "rescue", "lighthouse"} else "common",
                "location": "whiteboard",
                "category": "planning",
                "description": str(info.get("text") or ""),
                "objective": str(info.get("text") or ""),
                "agentAction": str(info.get("text") or ""),
                "reasoningSummary": "Readable-script story event.",
                "executionText": str(info.get("title") or event_id),
                "successText": "Story beat reached.",
                "failureText": "Story beat skipped.",
            },
        }
        campaign.replay_log.append(replay_event)
        self._append_event(campaign, event_type, {
            "story_event": info,
            "state_before": state_before,
            "state_after": state_after,
            "replay_event": replay_event,
        })

    def _emit_due_branch_scenes(self, campaign: CampaignSession, *, day: int) -> None:
        if day not in {8, 9, 10} or not campaign.branch_decision:
            return
        leaning = campaign.route_leaning or str(campaign.global_state.get("routeLeaning") or "contested")
        allowed = {"rescue", "lighthouse"} if leaning == "contested" or campaign.branch_policy == "both" else {leaning}
        for scene in BRANCH_SCENES:
            if int(scene.get("day") or 0) != day:
                continue
            branch = str(scene.get("branch") or "")
            if branch not in allowed:
                continue
            self._emit_story_replay(campaign, "branch_scene", scene, branch=branch)

    def _get_campaign(self, campaign_id: str) -> CampaignSession:
        if campaign_id not in self.sessions:
            raise KeyError(f"Unknown campaign: {campaign_id}")
        return self.sessions[campaign_id]

    def _planned_slots(self, campaign: CampaignSession) -> list[CampaignSlot]:
        return list(self.slots)

    def _ensure_branch_if_needed(self, campaign: CampaignSession) -> None:
        planned = self._planned_slots(campaign)
        if campaign.current_slot_index >= len(planned):
            return
        next_slot = planned[campaign.current_slot_index]
        if int(next_slot.day) < 8 or campaign.branch_decision:
            return
        if campaign.branch_policy == "both":
            campaign.selected_branch = "rescue"
            campaign.route_leaning = "rescue"
            campaign.branch_decision = {
                "chosen_branch": campaign.selected_branch,
                "routeLeaning": campaign.route_leaning,
                "reason": "both mode records rescue as the primary live route; use archived replay for counterfactual comparison",
            }
        elif campaign.branch_policy in {"rescue", "lighthouse"}:
            campaign.selected_branch = campaign.branch_policy  # type: ignore[assignment]
            campaign.route_leaning = campaign.selected_branch
            campaign.branch_decision = {
                "chosen_branch": campaign.selected_branch,
                "routeLeaning": campaign.route_leaning,
                "reason": f"forced by branch_policy={campaign.branch_policy}",
            }
        else:
            campaign.branch_decision = self._calculate_branch_decision(campaign)
            campaign.selected_branch = campaign.branch_decision["chosen_branch"]
            campaign.route_leaning = str(campaign.branch_decision.get("routeLeaning") or campaign.selected_branch)
        campaign.active_branch = campaign.selected_branch
        campaign.global_state["branch"] = campaign.selected_branch
        campaign.global_state["routeLeaning"] = campaign.route_leaning
        self._append_event(campaign, "branch_decided", {
            "branch_policy": campaign.branch_policy,
            "decision": jsonable(campaign.branch_decision),
            "chosen_branch": campaign.selected_branch,
            "routeLeaning": campaign.route_leaning,
            "global_state": jsonable(campaign.global_state),
        })
        self._emit_due_branch_scenes(campaign, day=int(next_slot.day))

    def _ensure_current_task(self, campaign: CampaignSession) -> None:
        if campaign.status == "complete" or (campaign.current_run() and campaign.current_run().status == "running"):
            return
        self._ensure_branch_if_needed(campaign)
        planned = self._planned_slots(campaign)
        if campaign.current_slot_index >= len(planned):
            self._finish_campaign(campaign)
            return
        slot = planned[campaign.current_slot_index]
        previous_day = campaign.global_state.get("day")
        previous_branch = campaign.global_state.get("branch")
        if campaign.branch_policy == "both" and slot.branch in {"rescue", "lighthouse"}:
            campaign.active_branch = slot.branch
            campaign.global_state["branch"] = slot.branch
        elif slot.branch != "common":
            campaign.active_branch = slot.branch
            campaign.global_state["branch"] = slot.branch
        campaign.global_state["day"] = slot.day
        if previous_day != slot.day:
            self._append_event(campaign, "day_changed", {
                "from_day": previous_day,
                "to_day": slot.day,
                "branch": campaign.global_state.get("branch"),
            })
            self._emit_due_branch_scenes(campaign, day=int(slot.day))
        if previous_branch != campaign.global_state.get("branch"):
            self._append_event(campaign, "branch_changed", {
                "from_branch": previous_branch,
                "to_branch": campaign.global_state.get("branch"),
                "day": slot.day,
            })
        task_id = self._select_task(campaign, slot)
        child = self.lan_service.create_session({
            "task_id": task_id,
            "agent_id": campaign.agent_id,
            "model_id": campaign.model_id,
            "max_steps": campaign.max_steps_per_task,
            "session_id": f"{campaign.campaign_id}-{slot.slot_id}-{uuid.uuid4().hex[:6]}",
        })
        campaign.current_session_id = child["session_id"]
        campaign.task_runs.append(CampaignTaskRun(
            slot_id=slot.slot_id,
            task_id=child["task_id"],
            session_id=child["session_id"],
            slug=child["slug"],
            title=child["title"],
        ))
        self._append_event(campaign, "task_started", {
            "slot": slot.public_dict(),
            "run": campaign.task_runs[-1].public_dict(),
            "global_state": jsonable(campaign.global_state),
        })
        campaign.updated_at = now_iso()

    def _select_task(self, campaign: CampaignSession, slot: CampaignSlot) -> str:
        if campaign.task_selection == "first" or len(slot.task_pool) == 1:
            return slot.task_pool[0]
        rng = random.Random(f"{campaign.seed}:{slot.slot_id}")
        return rng.choice(list(slot.task_pool))

    def _settle_current_run(self, campaign: CampaignSession, result: dict[str, Any]) -> None:
        run = campaign.current_run()
        if run is None or run.status != "running":
            return
        slot = self._slots_by_id[run.slot_id]
        score = float(result.get("score") or 0.0)
        run.status = self._outcome_for_score(score)
        run.score = score
        run.passed_all = bool(result.get("passed_all"))
        run.result = jsonable(result)
        run.finished_at = now_iso()
        delta = self._state_delta_for_result(slot, score)
        state_before = dict(campaign.global_state)
        self._apply_state_delta(campaign, delta, score)
        state_after = dict(campaign.global_state)
        campaign.completed_slots.append(slot.slot_id)
        for flag in getattr(slot, "flags", ()) or ():
            if flag not in campaign.story_flags:
                campaign.story_flags.append(flag)
        for unlock in getattr(slot, "unlocks", ()) or ():
            if unlock not in campaign.story_unlocks:
                campaign.story_unlocks.append(unlock)
        if result.get("failure_reasons"):
            for reason in result.get("failure_reasons") or []:
                text = str(reason)
                if text not in campaign.failure_reasons:
                    campaign.failure_reasons.append(text)
        replay_event = {
            "time": now_iso(),
            "day": slot.day,
            "branch": slot.branch,
            "slot_id": slot.slot_id,
            "slot_title": slot.story_title,
            "task_id": run.task_id,
            "task_title": run.title,
            "session_id": run.session_id,
                "score": score,
                "passed_all": run.passed_all,
                "outcome": run.status,
                "state_delta": delta,
                "failure_reasons": result.get("failure_reasons") or [],
                "story_flags": list(getattr(slot, "flags", ()) or ()),
                "story_unlocks": list(getattr(slot, "unlocks", ()) or ()),
                "state_before": state_before,
                "state_after": state_after,
                "phase_hint": "replay_logged",
                "frontend_task": {
                    "id": slot.slot_id,
                "real_task_id": run.task_id,
                    "title": slot.story_title,
                    "day": slot.day,
                    "branch": campaign.global_state.get("branch") if campaign.global_state.get("branch") in {"common", "rescue", "lighthouse"} else slot.branch,
                    "location": slot.location,
                    "category": "planning",
                    "description": run.title,
                    "objective": f"{slot.slot_id} · {slot.story_title}，映射真实任务 {run.task_id}",
                    "agentAction": f"Agent submitted {run.task_id} with score {score}",
                    "reasoningSummary": getattr(slot, "script_role", "") or "Live campaign result from backend agent trace.",
                    "executionText": f"Executing {run.task_id}",
                    "successText": "Campaign slot succeeded.",
                    "failureText": "Campaign slot failed or remained incomplete.",
            },
        }
        campaign.replay_log.append(replay_event)
        self._append_event(campaign, "slot_completed", {
            "slot_id": slot.slot_id,
            "task_id": run.task_id,
            "session_id": run.session_id,
            "score": score,
            "outcome": run.status,
            "state_before": state_before,
            "state_after": state_after,
            "replay_event": replay_event,
        })
        campaign.updated_at = now_iso()

    def _advance_after_settlement(self, campaign: CampaignSession) -> None:
        current = campaign.current_run()
        if current and current.status == "running":
            return
        campaign.current_session_id = ""
        campaign.current_slot_index += 1
        self._ensure_current_task(campaign)

    def _state_delta_for_result(self, slot: CampaignSlot, score: float) -> dict[str, int]:
        if score >= 85:
            bucket = "success"
        elif score >= 60:
            bucket = "partial"
        elif score > 0:
            bucket = "failure"
        else:
            bucket = "missing"
        if getattr(slot, "outcome_deltas", None):
            return dict(slot.outcome_deltas.get(bucket) or {})
        if bucket == "success":
            scale = 1.0
        elif bucket == "partial":
            scale = 0.5
        elif bucket == "failure":
            scale = -0.35
        else:
            scale = -0.75
        return {key: int(round(value * scale)) for key, value in slot.state_delta.items()}

    def _apply_state_delta(self, campaign: CampaignSession, delta: dict[str, int], score: float) -> None:
        for key, value in delta.items():
            campaign.global_state[key] = _clamp_metric(float(campaign.global_state.get(key, 0)) + value)
        if score < 60:
            campaign.global_state["failure_stage"] = int(campaign.global_state.get("failure_stage", 0)) + 1
            campaign.global_state["recovery_window"] = max(0, int(campaign.global_state.get("recovery_window", 0)) - 1)
            campaign.global_state["dissatisfaction"] = _clamp_metric(float(campaign.global_state.get("dissatisfaction", 0)) + 4)
        elif score >= 85:
            campaign.global_state["recovery_window"] = min(4, int(campaign.global_state.get("recovery_window", 0)) + 1)
            campaign.global_state["dissatisfaction"] = _clamp_metric(float(campaign.global_state.get("dissatisfaction", 0)) - 2)
        if campaign.global_state.get("failure_stage", 0) >= 3:
            campaign.global_state["pressure_level"] = "pressure"

    def _calculate_branch_decision(self, campaign: CampaignSession) -> dict[str, Any]:
        state = campaign.global_state
        rescue_utility = (
            state.get("signal", 0) * 0.25
            + state.get("rescue_confidence", 0) * 0.25
            + state.get("blue_zone_evidence", 0) * 0.2
            + state.get("route_confidence", 0) * 0.15
            + state.get("trust", 0) * 0.15
            - state.get("outside_risk", 0) * 0.08
        )
        lighthouse_utility = (
            state.get("autonomy_readiness", 0) * 0.25
            + state.get("storm_readiness", 0) * 0.25
            + state.get("safety", 0) * 0.2
            + state.get("trust", 0) * 0.15
            + state.get("morale", 0) * 0.15
            - state.get("maintenance_debt", 0) * 0.05
        )
        gap = rescue_utility - lighthouse_utility
        route_leaning = "contested" if abs(gap) < 3 else ("rescue" if gap > 0 else "lighthouse")
        chosen = "rescue" if route_leaning == "rescue" else "lighthouse"
        return {
            "rescue_utility": round(rescue_utility, 2),
            "lighthouse_utility": round(lighthouse_utility, 2),
            "chosen_branch": chosen,
            "routeLeaning": route_leaning,
            "reason": "utility is advisory; routeLeaning drives branch scenes while Day8-11 common tasks continue",
        }

    def _outcome_for_score(self, score: float) -> str:
        if score >= 85:
            return "success"
        if score >= 60:
            return "partial"
        if score > 0:
            return "failed"
        return "missing"

    def _finish_campaign(self, campaign: CampaignSession) -> None:
        campaign.status = "complete"
        campaign.global_state["day"] = FINAL_AUDIT_EVENT["day"]
        self._emit_story_replay(campaign, "final_audit", FINAL_AUDIT_EVENT)
        ending_key = self._resolve_ending_key(campaign.global_state)
        ending = ENDINGS[ending_key]
        branch = "rescue" if ending_key == "rescue" else "lighthouse" if ending_key == "lighthouse" else "common"
        title = str(ending["title"])
        text = str(ending["text"])
        if campaign.global_state.get("failure_stage", 0) >= 5 and ending_key in {"rescue", "lighthouse"}:
            title = f"{title} · 高风险"
            text += " 多次任务失败使成功线带有明显高风险标记。"
        campaign.ending = {
            "title": title,
            "text": text,
            "branch": branch,
            "ending_key": ending_key,
            "audit": self._final_audit_summary(campaign.global_state),
        }
        campaign.current_session_id = ""
        self._append_event(campaign, "campaign_complete", {
            "ending": campaign.ending,
            "global_state": jsonable(campaign.global_state),
        })
        campaign.updated_at = now_iso()

    def _resolve_ending_key(self, state: dict[str, Any]) -> str:
        if state.get("dissatisfaction", 0) >= 80:
            return "aura_destroyed"
        if state.get("trust", 100) <= 18:
            return "aura_removed"
        if (
            state.get("water", 100) <= 15
            or state.get("medicine", 100) <= 12
            or state.get("safety", 100) <= 15
            or state.get("morale", 100) <= 12
            or state.get("failure_stage", 0) >= 10
        ):
            return "decline"
        if (
            state.get("routeLeaning") == "rescue"
            and state.get("rescue_confidence", 0) >= 30
            and state.get("blue_zone_evidence", 0) >= 8
            and state.get("route_confidence", 0) >= 25
        ):
            return "rescue"
        if (
            state.get("routeLeaning") == "lighthouse"
            and state.get("storm_readiness", 0) >= 35
            and state.get("autonomy_readiness", 0) >= 28
        ):
            return "lighthouse"
        if state.get("routeLeaning") == "rescue" and state.get("rescue_confidence", 0) >= state.get("autonomy_readiness", 0):
            return "rescue"
        if state.get("routeLeaning") == "lighthouse":
            return "lighthouse"
        return "decline" if state.get("failure_stage", 0) >= 6 else "lighthouse"

    def _final_audit_summary(self, state: dict[str, Any]) -> dict[str, Any]:
        keys = [
            "water", "medicine", "trust", "safety", "signal", "morale",
            "routeLeaning", "rescue_confidence", "blue_zone_evidence",
            "autonomy_readiness", "storm_readiness", "failure_stage",
            "dissatisfaction", "pressure_level",
        ]
        return {key: state.get(key) for key in keys}

    def _campaign_dir(self, campaign: CampaignSession) -> Path:
        return self.run_dir / campaign.campaign_id

    def _persist_campaign(self, campaign: CampaignSession) -> None:
        campaign_dir = self._campaign_dir(campaign)
        campaign_dir.mkdir(parents=True, exist_ok=True)
        (campaign_dir / "campaign.json").write_text(
            json.dumps(self.trace_campaign(campaign.campaign_id), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (campaign_dir / "report.html").write_text(
            self.render_report(campaign.campaign_id),
            encoding="utf-8",
        )
