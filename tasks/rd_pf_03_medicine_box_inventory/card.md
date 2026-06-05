# RD-PF-03 · 混乱药箱盘点

> **类别**: Productivity Flow · 避难所资料运营　|　**形态**: pure-text

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 01_task_3 · Recover Official arXiv Titles and BibTeX from Local PDFs |
| **保留能力** | PDF/图像识别 / 元数据恢复 / 重命名 |

## Red Dust 场景

邻居翻出 21 份药品说明书和药盒照片，文件名全乱，部分缺页。

## 一眼胜负

识别每种药、剂量、禁忌和有效期，生成药箱清单并把危险药隔离。

## 可看懂轨迹

`读药盒 → 查说明书 → 标剂量 → 隔离过期药 → 生成清单`

## 可见状态 / Grader

药品数量匹配；过期/禁忌药进隔离盒；小铁可用药正确；未给出危险剂量。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D01-T02` · 紧急资源清点
- **剧本日**: Day 1
- **剧情作用**: 建立公开库存和人工复核基础
- **Flags**: `inventory_auditable`
- **Unlocks**: `public_inventory_board`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
