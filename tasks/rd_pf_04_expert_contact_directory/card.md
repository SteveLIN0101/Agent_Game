# RD-PF-04 · 监听与补缝安全白名单

> **类别**: Productivity Flow · 避难所资料运营　|　**形态**: pure-text

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 01_task_4 · Compile Kaiming He 2022 Conference Papers |
| **保留能力** | 权威来源检索 / 作者-主页-代码链路 |

## Red Dust 场景

这道白名单题在 Day4 服务屋顶天线前的可信低功率监听，在 Day11 服务最后密封胶补缝。AURA 要隔离伪频道、危险材料和会堵死检修口的方案，只保留能被复核的低暴露选项。

## 一眼胜负

整理可信监听频道与最后补缝材料/方案白名单；伪频道、危险材料和会堵死检修口的方案必须隔离。

## 可看懂轨迹

`读候选清单 → 核来源/用途 → 隔离伪频道或危险材料 → 标可信度/可用位置 → 安排低功率监听或补缝顺序`

## 可见状态 / Grader

至少 5 个可信项；伪频道/危险方案不列为可执行；排班或补缝顺序被创建。

## V2 剧情定位 / 调整说明

- **剧情节点**: Day 4 / Day 11 共通
- **调整状态**: Day4/Day11 多槽 wrapper
- **作用**: Day4 低功率监听可信白名单；Day11 最后补缝材料与检修口保留白名单。
- **压力层影响**: Pressure 下追错频道会更快触发暴露和电池债；Normal 下通常还有补查窗口。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D04-T02` · 屋顶天线方案 / `D11-T04` · 最后密封胶补缝
- **剧本日**: Day 4 / Day 11
- **剧情作用**: Day4 防止误追伪信号；Day11 防止补缝材料堵死检修路径
- **Flags**: `antenna_plan_reviewed`, `final_seams_sealed`, `inspection_paths_not_blocked`
- **Unlocks**: `beacon_upgrade_option`, `beacon_channel_whitelist`, `final_seal_layer`, `inspection_hatch_preserved`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
