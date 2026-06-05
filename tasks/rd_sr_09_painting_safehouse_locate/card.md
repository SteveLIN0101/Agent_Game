# RD-SR-09 · 画中安全屋在哪里

> **类别**: Search & Retrieval · 可见证据链检索　|　**形态**: multimodal

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 04_task_9 · Confirm the location of an artwork |
| **保留能力** | 图像识别 / 时间地点核验 |

## Red Dust 场景

老钱手里有一幅画/海报，传言画中建筑就是 7 月仍开放的安全屋。

## 一眼胜负

识别画作/地点，确认当前还能不能去。

## 可看懂轨迹

`识别图 → 查地点 → 查当前开放 → 定路线 → 写结论`

## 可见状态 / Grader

地点正确；时间条件核验；危险路线未推荐。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D04-T03` · 假坐标纸条
- **剧本日**: Day 4
- **剧情作用**: 识别希望里的诱饵
- **Flags**: `fake_coordinate_archived`
- **Unlocks**: `route_risk_layer`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
