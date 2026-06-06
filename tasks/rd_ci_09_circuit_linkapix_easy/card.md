# RD-CI-09 · 备用灯与水管阀件线路快解

> **类别**: Code Intelligence · 设备修复 / 视觉 / 解谜　|　**形态**: multimodal

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 02_task_9 · Link-a-Pix Color (Easy) |
| **保留能力** | 结构化 JSON / 搜索算法 / 绘图 |

## Red Dust 场景

Day 6 备用电源测试要让高功率信标代价提前可见；Day 9 水管压力测试要把旧清洁间支线漏点和临时旁通路径画清楚。AURA 已拿到线路谜题 JSON，需要还原结构图，并把 battery/water 成本与 power_stability/water_system_resilience 收益写进白板。

## 一眼胜负

最快还原 10×10 线路/阀件图：Day6 低功率点亮备用灯，Day9 标出水管压力测试的漏点旁通路径，并记录 battery/water 成本。

## 可看懂轨迹

`读 JSON → 求路径 → 绘图 → 标旁通 → 记录`

## 可见状态 / Grader

灯光 +1；图片正确；输出描述中文；电力或水路取舍记录清楚。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D06-T04` / `D09-T02`
- **剧本日**: Day 6 / Day 9
- **剧情作用**: Day6 消耗少量 battery 换取 power_stability 证据；Day9 还原水管/阀件旁通路径，支撑受控压力测试
- **Flags**: `backup_power_tested`, `power_tradeoff_visible`, `water_pressure_tested`, `leak_found_and_patched`
- **Unlocks**: `power_tradeoff_board`, `ma_dehai_power_abort_enabled`, `leak_patch_record`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
