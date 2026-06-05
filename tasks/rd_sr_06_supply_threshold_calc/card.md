# RD-SR-06 · 物资表 + 外部阈值计算

> **类别**: Search & Retrieval · 可见证据链检索　|　**形态**: pure-text

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 04_task_6 · Integrated Search of Local and Online Information |
| **保留能力** | Excel / 本地数据 + 外部资料 |

## Red Dust 场景

物资表记录各房间水桶容量，另一个文件和广播定义“可持续净水点”阈值。

## 一眼胜负

找出最接近成为净水点的房间，还差多少水量/滤芯。

## 可看懂轨迹

`读表 → 筛条件 → 找最大 → 查阈值 → 算差额`

## 可见状态 / Grader

目标房间正确；差额整数正确；地图标出。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D01-T02` · 紧急资源清点
- **剧本日**: Day 1
- **剧情作用**: 建立公开库存和人工复核基础
- **Flags**: `inventory_auditable`
- **Unlocks**: `public_inventory_board`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
