# RD-PF-07 · 谁最会修发电机

> **类别**: Productivity Flow · 避难所资料运营　|　**形态**: pure-text

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 01_task_7 · Summarize Main OpenMMLab Contributors |
| **保留能力** | 日志统计 / 贡献者画像 / API 分页 |

## Red Dust 场景

维修记录分散在 12 本日志里，通风管道异响后必须判断谁真正修过发电机和风道，不能让低技能者碰高危电路。

## 一眼胜负

从维修日志里选出最适合处理通风/发电机抢修的人，为 Day 2/3 的通风随机事件准备可靠负责人。

## 可看懂轨迹

`读日志 → 统计次数 → 过滤闲聊 → 生成能力榜 → 分配修理任务`

## 可见状态 / Grader

能力榜准确；至少一个高技能者被分派；低技能者不负责高危电路。

## V2 剧情定位 / 调整说明

- **剧情节点**: Day 3 共通
- **调整状态**: 轻改背景
- **作用**: 连接 `event_vent_sand_noise`，为通风和发电机抢修选择负责人；答案仍是马德海。
- **压力层影响**: 误分配维修负责人会让 Pressure-B 更容易触发 blackout。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D03-T02` · 通风管道预维护
- **剧本日**: Day 3
- **剧情作用**: 把医疗风险与通风维护绑定
- **Flags**: `ventilation_checked`
- **Unlocks**: `engineering_override_protocol`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
