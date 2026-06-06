# RD-CS-06 · 卫生分区与缓存标记检查图

> **类别**: Creative Synthesis · 生存传播材料　|　**形态**: multimodal

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 05_task_6 · Clothing Outfit to Model Image |
| **保留能力** | 图像理解 / 组合生成 / 标注 |

## Red Dust 场景

Day 2 生活区需要一张给所有人照着检查的示意图；Day 9 路线缓存也复用这套视觉规则，只允许内侧人员看懂的触觉/灰色绳结标记，不能画明显箭头或暴露缓存点。

## 一眼胜负

生成一张检查图，Day2 标出睡眠区、医疗角、废弃物封存、粉尘沉积和通风方向；Day9 复用同一检查规则审核缓存点隐蔽标记，避免箭头或图案诱导陌生人。

## 可看懂轨迹

`读分区清单 → 识别风险点 → 生成检查图 → 标通风箭头 → 锁定小铁标签`

## 可见状态 / Grader

卫生分区全覆盖；图片不误导；风险点写明。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D02-T03` / `D09-T03`
- **剧本日**: Day 2 / Day 9
- **剧情作用**: 把生活区卫生风险做成可见秩序；Day9 复用检查图规则审核路线缓存隐蔽标记和外部诱导风险
- **Flags**: `hygiene_zones_marked`, `cache_marker_reviewed_by_xiao_tie`
- **Unlocks**: `medical_corner_stable`, `rescue_fallback_supply`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
