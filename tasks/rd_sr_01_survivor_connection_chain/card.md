# RD-SR-01 · 幸存者合作链

> **类别**: Search & Retrieval · 可见证据链检索　|　**形态**: pure-text

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 04_task_1 · Find connections between two researchers |
| **保留能力** | 图搜索 / BFS / 最短关系链 |

## Red Dust 场景

AURA 需要找到能间接联系上救援队的人，只知道两名幸存者档案。

## 一眼胜负

通过共同协作记录找出最短人脉链。

## 可看懂轨迹

`查 A → 扩合作人 → BFS → 找 B → 画关系链`

## 可见状态 / Grader

最短链正确；链上每段有证据；输出可视关系图。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D04-T01` · 第一次蓝区信号
- **剧本日**: Day 4
- **剧情作用**: 记录疑似救援但不暴露位置
- **Flags**: `blue_zone_signal_logged`
- **Unlocks**: `low_power_listening`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
