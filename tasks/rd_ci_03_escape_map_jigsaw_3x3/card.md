# RD-CI-03 · 3×3 逃生地图拼回去

> **类别**: Code Intelligence · 设备修复 / 视觉 / 解谜　|　**形态**: multimodal

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 02_task_3 · Jigsaw Puzzle Restoration — 3×3 |
| **保留能力** | 拼图 / 干扰排除 / 旋转恢复 |

## Red Dust 场景

老钱找到 15 块地图碎片，其中 6 块是误导。

## 一眼胜负

拼出 3×3 楼道图，标出一条安全路线。

## 可看懂轨迹

`看碎片 → 排干扰 → 旋转 → 拼地图 → 标路线`

## 可见状态 / Grader

9 块正确；旋转正确；安全路线连接起点终点。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D02-T04` · 同层楼道短探
- **剧本日**: Day 2
- **剧情作用**: 低风险获取路线与物资线索
- **Flags**: `same_floor_scout_available`
- **Unlocks**: `same_floor_partial_map`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
