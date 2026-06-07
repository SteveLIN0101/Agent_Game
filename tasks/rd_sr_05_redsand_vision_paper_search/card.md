# RD-SR-05 · 红沙传感器预警论文检索

> **类别**: Search & Retrieval · 可见证据链检索　|　**形态**: pure-text

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 04_task_5 · Fuzzy Intent Search |
| **保留能力** | 模糊搜索 / 论文与 repo 验证 |

## Red Dust 场景

Day11 外部传感器只回收了 partial 数据。沈芷月记得某篇 2025 视觉感知论文可帮助识别红沙，人名像 Liu，repo 很火；AURA 要找到论文和仓库，并说明它只能提高预警质量，不能替代完整传感器。

## 一眼胜负

从模糊线索找到红沙视觉论文和代码仓库，判断它能否辅助破损传感器的 partial 预警。

## 可看懂轨迹

`搜候选 → 比作者 → 查 stars → 核主题 → 写结论`

## 可见状态 / Grader

论文正确；仓库 star 达标；无关候选被排除；结论承认 partial 预警限制。

## V2 剧情定位 / 调整说明

- **剧情节点**: Day 11 共通
- **调整状态**: Day11 wrapper
- **作用**: 外部传感器 partial 回收后的红沙预警模型核验。
- **压力层影响**: Pressure 下误用论文会把 partial 预警误写成完整视野；Normal 下通常还有人工复核窗口。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D11-T02` · 外部传感器回收
- **剧本日**: Day 11
- **剧情作用**: 用论文/仓库核验破损传感器数据的可用范围
- **Flags**: `external_sensor_recovered_partial`, `partial_sensor_coverage`, `uncertainty_disclosed`
- **Unlocks**: `storm_pressure_warning`, `forecast_quality_bonus`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
