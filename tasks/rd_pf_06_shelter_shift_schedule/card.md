# RD-PF-06 · 配给、值守与低功率窗口表

> **类别**: Productivity Flow · 避难所资料运营　|　**形态**: pure-text

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 01_task_6 · Calendar Conflict Detection and Smart Scheduling |
| **保留能力** | 日历冲突 / 优化调度 / 决策日志 |

## Red Dust 场景

这道排程题服务 Day 2 配给与值守试运行，也服务 Day 10 低功率日程。AURA 要把公共水药、守门、修机、休息、医疗复核、通信监听和净水/通风窗口排进表里；私人物资不能直接征用，医疗照明和异常频段唤醒要保留人工复核。

## 一眼胜负

排出守门、取水、修机、休息、配给复核和低功率监听/净水/通风窗口，优先照顾病人、维修者、外出者例外规则和人工异议。

## 可看懂轨迹

`看体力和私人物资边界 → 查风险窗口 → 排班 → 发现复核冲突 → 改班并解释`

## 可见状态 / Grader

每人休息达标；小铁不被派外出；夜间有人守门；任务优先级最大化。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D02-T01` · 配给与值守试运行；`D10-T01` · 低功率日程
- **剧本日**: Day 2 / Day 10
- **剧情作用**: 从私人物品进入公共配给和值守规则，并在 Day10 将净水、通风、医疗照明和监听窗口纳入低耗排程
- **Flags**: `ration_trial_started`
- **Unlocks**: `ration_trial_board`, `low_power_schedule`, `critical_window_timetable`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
