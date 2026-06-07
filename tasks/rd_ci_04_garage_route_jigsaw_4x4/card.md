# RD-CI-04 · 4×4 车库边缘探头图

> **类别**: Code Intelligence · 设备修复 / 视觉 / 解谜　|　**形态**: multimodal

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 02_task_4 · Medium Jigsaw Puzzle — 4×4 |
| **保留能力** | 更大拼图 / 全局优化 |

## Red Dust 场景

这道拼图题服务 Day 4 假坐标纸条核验，也服务 Day 10 地下车库边缘侦察。地下车库探头图被切成 24 块，8 块是偏移裁切干扰；AURA 只能标出风险和候选路线，不能把车库写成已确认可走。

## 一眼胜负

拼出车库探头图，标出红沙堆积、坍塌和右侧检修门候选；不得把候选通道写成已确认安全路线。

## 可看懂轨迹

`算边缘 → 搜全局 → 拼图 → 标坍塌和红沙风险 → 生成候选路线`

## 可见状态 / Grader

16 块正确；通道连通；风险点标注。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D04-T03` · 假坐标纸条；`D10-T04` · 地下车库边缘侦察
- **剧本日**: Day 4 / Day 10
- **剧情作用**: 识别希望里的诱饵，并在 Day10 只确认候选路线而非安全路线
- **Flags**: `fake_coordinate_archived`
- **Unlocks**: `route_risk_layer`, `garage_edge_scan`, `garage_service_door_candidate`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
