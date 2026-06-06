# RD-SR-06 · 公共水量阈值与储水差额计算

> **类别**: Search & Retrieval · 可见证据链检索　|　**形态**: pure-text

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 04_task_6 · Integrated Search of Local and Online Information |
| **保留能力** | Excel / 本地数据 + 外部资料 |

## Red Dust 场景

公共水量计算可服务 Day1 资源清点、Day5 空桶储水计划和后续泵房探索。AURA 要把公共资源和私人物资分开，计算可持续净水/储水差额，标注来源、复核人，并说明涉及水桶搬运或滤芯更换时必须经过马德海工具权限确认。

## 一眼胜负

从公共物资表中找出最接近成为净水/储水节点的房间，计算差额，并标注来源、复核人与马德海工具权限。

## 可看懂轨迹

`读表 → 区分公共/私人 → 找最大 → 查阈值 → 算差额并标来源`

## 可见状态 / Grader

目标房间正确；差额整数正确；地图标出；来源/复核人/工具权限清楚。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D01-T02` / `D05-T04` / `D08-T04`
- **剧本日**: Day 1 / Day 5 / Day 8
- **剧情作用**: 计算公共水量阈值，服务资源清点、空桶储水和泵房探索
- **Flags**: `inventory_auditable`, `water_storage_plan_ready`
- **Unlocks**: `public_inventory_board`, `sealed_water_cache`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
