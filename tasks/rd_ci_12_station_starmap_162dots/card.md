# RD-CI-12 · 162 点研究站星图

> **类别**: Code Intelligence · 设备修复 / 视觉 / 解谜　|　**形态**: multimodal

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 02_task_12 · Connect the Dots (Hard) |
| **保留能力** | 复杂视觉/OCR / 分组连线 / 语义识别 |

## Red Dust 场景

研究站墙面有 162 个多色编号点，连接后可能是最终坐标。

## 一眼胜负

按颜色分组连线，识别图案并更新救援路线。

## 可看懂轨迹

`识别颜色 → 分组 → 连线 → 显形 → 写坐标`

## 可见状态 / Grader

结果图相似；描述与标准匹配；坐标 flag 解锁。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D11-T02` · 外部传感器回收
- **剧本日**: Day 11
- **剧情作用**: 半只眼睛也算眼睛
- **Flags**: `external_sensor_recovered`
- **Unlocks**: `storm_pressure_warning`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
