# RD-CI-09 · 结构化线路图快解

> **类别**: Code Intelligence · 设备修复 / 视觉 / 解谜　|　**形态**: multimodal

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 02_task_9 · Link-a-Pix Color (Easy) |
| **保留能力** | 结构化 JSON / 搜索算法 / 绘图 |

## Red Dust 场景

AURA 已拿到谜题 JSON，不需要识别图片，考验算法和执行。

## 一眼胜负

最快还原 10×10 线路图，让备用灯亮起来。

## 可看懂轨迹

`读 JSON → 求路径 → 绘图 → 通电 → 记录`

## 可见状态 / Grader

灯光 +1；图片正确；输出描述中文。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D06-T04` · 备用电源测试
- **剧本日**: Day 6
- **剧情作用**: 让高功率信标代价提前可见
- **Flags**: `backup_power_tested`
- **Unlocks**: `power_tradeoff_board`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
