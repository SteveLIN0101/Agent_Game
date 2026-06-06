# RD-PF-02 · 净水、空桶与水压测试说明书还原

> **类别**: Productivity Flow · 避难所资料运营　|　**形态**: pure-text

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 01_task_2 · Recover Original Table TeX from arXiv Source |
| **保留能力** | 源文件恢复 / 表格抽取 / 精确复制 |

## Red Dust 场景

净水器、储水桶和旧水管说明书被潮气和红沙弄坏，只剩压缩包、碎片图片和散乱表格。它可服务 Day2 滤芯清洗、Day5 空桶消毒储水、Day8 泵房材料和 Day9 水管压力测试；Day9 必须保留医疗角最低用水，并记录受控漏点而非夸大成永久修复。

## 一眼胜负

还原滤芯安装表、冲洗顺序、空桶消毒流程和水压测试步骤，让观众看到“表格恢复 → 装置可安全储水/受控试压”。

## 可看懂轨迹

`解包 → 识别表格 → 还原顺序 → 交给维修台 → 试运行`

## 可见状态 / Grader

安装/冲洗步骤顺序正确；滤芯寿命 +2 天；空桶消毒标记清楚；没有把错误表格贴到白板。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D02-T02` / `D05-T04` / `D08-T04` / `D09-T02`
- **剧本日**: Day 2 / Day 5 / Day 8 / Day 9
- **剧情作用**: 还原净水/储水/泵房/水压测试流程，支撑滤芯清洗、空桶储水和 Day9 受控压力测试
- **Flags**: `water_filter_checked`, `water_storage_plan_ready`, `water_pressure_tested`, `leak_found_and_patched`
- **Unlocks**: `water_low_power_mode`, `sealed_water_cache`, `leak_patch_record`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
