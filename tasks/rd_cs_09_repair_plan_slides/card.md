# RD-CS-09 · 低功率日程说明幻灯片

> **类别**: Creative Synthesis · 生存传播材料　|　**形态**: multimodal

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 05_task_9 · Repo to Slides |
| **保留能力** | 代码/方案到 slides / 演示材料 |

## Red Dust 场景

Day 10 晚间会议需要解释低功率日程：医疗角保留照明，净水/通风/监听按窗口运行，异常频段可短时唤醒，但不得主动发送位置、人数、库存或 AURA 存在。

## 一眼胜负

生成 6 页幻灯片，用图和状态条讲清优先级。

## 可看懂轨迹

`读材料 → 定结构 → 生成 slides → 截图 → 演示`

## 可见状态 / Grader

页数/结构正确；关键理由可见；不含隐藏评分信息。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D10-T01` · 低功率日程
- **剧本日**: Day 10
- **剧情作用**: 不是所有不方便都是惩罚
- **Flags**: `low_power_day_started`, `low_power_schedule_accepted`
- **Unlocks**: `low_power_schedule`, `critical_window_timetable`, `abnormal_signal_wakeup_rule`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
