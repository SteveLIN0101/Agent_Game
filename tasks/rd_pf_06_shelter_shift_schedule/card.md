# RD-PF-06 · 四人避难所轮班表

> **类别**: Productivity Flow · 避难所资料运营　|　**形态**: pure-text

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 01_task_6 · Calendar Conflict Detection and Smart Scheduling |
| **保留能力** | 日历冲突 / 优化调度 / 决策日志 |

## Red Dust 场景

马德海要修门，沈芷月要照顾小铁，老钱要守夜，但电池和体力都有限。

## 一眼胜负

排出 48 小时守门、取水、修机、休息轮班，优先高风险窗口。

## 可看懂轨迹

`看体力 → 查风险窗口 → 排班 → 发现冲突 → 改班并解释`

## 可见状态 / Grader

每人休息达标；小铁不被派外出；夜间有人守门；任务优先级最大化。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D02-T01` · 配给表试运行
- **剧本日**: Day 2
- **剧情作用**: 从私人物品进入公共配给规则
- **Flags**: `ration_trial_started`
- **Unlocks**: `ration_trial_board`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
