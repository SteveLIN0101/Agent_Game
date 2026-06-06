# RD-CI-09 · 结构化线路图快解

> **类别**: Code Intelligence · 设备修复 / 视觉 / 解谜　|　**形态**: multimodal

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 02_task_9 · Link-a-Pix Color (Easy) |
| **保留能力** | 结构化 JSON / 搜索算法 / 绘图 |

## Red Dust 场景

Day 6 备用电源测试要让高功率信标代价提前可见。AURA 已拿到线路谜题 JSON，需要低功率还原线路图、点亮备用灯，并把 battery 消耗与 power_stability 收益写进白板。

## 一眼胜负

最快还原 10×10 线路图，低功率点亮备用灯，并记录 battery 消耗与 power_stability 收益。

## 可看懂轨迹

`读 JSON → 求路径 → 绘图 → 通电 → 记录`

## 可见状态 / Grader

灯光 +1；图片正确；输出描述中文；电力取舍记录清楚。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D06-T04` · 备用电源测试
- **剧本日**: Day 6
- **剧情作用**: 消耗少量 battery 换取 power_stability 证据，让高功率信标代价提前可见
- **Flags**: `backup_power_tested`, `power_tradeoff_visible`
- **Unlocks**: `power_tradeoff_board`, `ma_dehai_power_abort_enabled`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
