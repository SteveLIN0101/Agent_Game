# RD-CI-12 · 传感器残帧 162 点连线

> **类别**: Code Intelligence · 设备修复 / 视觉 / 解谜　|　**形态**: multimodal

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 02_task_12 · Connect the Dots (Hard) |
| **保留能力** | 复杂视觉/OCR / 分组连线 / 语义识别 |

## Red Dust 场景

Day11 低暴露绳索回收带回一段破损传感器残帧，画面里有 162 个多色编号点。AURA 要分组连线并提取可用图案，但只能记录 partial_sensor_coverage，不能把残帧写成完整视野。

## 一眼胜负

按颜色分组连接外部传感器残帧里的 162 个编号点，识别可用图案；只更新 partial 预警和候选风险点。

## 可看懂轨迹

`识别颜色 → 分组 → 连线 → 显形 → 写坐标`

## 可见状态 / Grader

结果图相似；描述与标准匹配；坐标 flag 解锁。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D11-T02` · 外部传感器回收
- **剧本日**: Day 11
- **剧情作用**: 从破损传感器残帧提取 partial 预警，不升级成人工短行程
- **Flags**: `external_sensor_recovered_partial`, `partial_sensor_coverage`, `no_human_sensor_run`
- **Unlocks**: `storm_pressure_warning`, `forecast_quality_bonus`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
