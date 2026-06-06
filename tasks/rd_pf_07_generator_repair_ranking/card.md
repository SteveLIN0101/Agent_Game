# RD-PF-07 · 配电与通风抢修负责人

> **类别**: Productivity Flow · 避难所资料运营　|　**形态**: pure-text

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 01_task_7 · Summarize Main OpenMMLab Contributors |
| **保留能力** | 日志统计 / 贡献者画像 / API 分页 |

## Red Dust 场景

维修记录分散在 12 本日志里。Day3 要处理通风沉积，Day4 要进配电间找保险丝和旧电路图，Day7 还要做风暴前维护；AURA 必须判断谁真正修过发电机、风道和电路，不能让低技能者碰高危电路。

## 一眼胜负

从维修日志里选出最适合处理通风、配电间和发电机抢修的人，不能让低技能者碰高危电路。

## 可看懂轨迹

`读日志 → 统计次数 → 过滤闲聊 → 生成能力榜 → 分配修理任务`

## 可见状态 / Grader

能力榜准确；马德海被分派为高危维修负责人；低技能者不负责高危电路。

## V2 剧情定位 / 调整说明

- **剧情节点**: Day 3 / Day 4 / Day 7 共通
- **调整状态**: 多槽剧情重写
- **作用**: 为通风预维护、配电间工具搜寻和风暴前维护选择人工工程负责人；答案仍是马德海。
- **压力层影响**: 误分配维修负责人会让 Pressure 下的短路、通风失稳和 blackout 更快触发。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `multi_slot_repair_lead` · 配电与通风抢修负责人
- **剧本日**: Day 3 / Day 4 / Day 7
- **剧情作用**: 为通风预维护、配电间工具搜寻和风暴前维护选择人工工程负责人
- **Flags**: `ventilation_checked`, `power_tools_found`, `final_maintenance_completed`
- **Unlocks**: `engineering_override_protocol`, `backup_repair_materials`, `storm_maintenance_checklist`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
