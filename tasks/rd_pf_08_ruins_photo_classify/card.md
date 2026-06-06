# RD-PF-08 · 近门与楼道监控截图五分类

> **类别**: Productivity Flow · 避难所资料运营　|　**形态**: multimodal

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 01_task_8 · Classify Mixed Images into 5 Categories |
| **保留能力** | 多模态分类 / 文件组织 |

## Red Dust 场景

AURA 不能让小铁靠近门或独自深入楼道，只能读取近门/楼道监控截图，把遗落包裹、危险红沙区、医疗可用、可走路线和无关噪声分类上图，为 Day1 近门搜寻和 Day5 条件短探设置撤回条件。

## 一眼胜负

把近门/楼道监控截图分成遗落包裹、危险红沙区、医疗可用、可走路线和无关噪声，并标到风险图上。

## 可看懂轨迹

`解包监控截图 → 逐张识别 → 建风险文件夹 → 上近门地图 → 抽查红沙区`

## 可见状态 / Grader

截图唯一归类；危险/水源两类准确率高；近门地图点位与分类一致。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D01-T04` / `D05-T01`
- **剧本日**: Day 1 / Day 5
- **剧情作用**: 用监控截图支撑近门搜寻和 Day5 条件短探，避免人员冒进
- **Flags**: `near_door_loot_checked`, `hallway_supply_checked`
- **Unlocks**: `xiao_tie_observation_role`, `corridor_supply_notes`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
