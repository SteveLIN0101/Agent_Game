# RD-PF-01 · 储藏架与库存风险公告分拣

> **类别**: Productivity Flow · 避难所资料运营　|　**形态**: pure-text

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 01_task_1 · ArXiv Daily Paper Digest |
| **保留能力** | 多源资料抓取 / 分类 / 推荐 |

## Red Dust 场景

Day9 深层储藏架加固被标记为 deferred-with-warning；Day11 最终库存封存前，AURA 收到 36 条电台片段、纸质公告照片和楼内传言，需要筛出真正可执行的信息，并把未完成维护债务与谣言隔离开。

## 一眼胜负

把公告、盘点照片和楼内传言分成水源、医疗、路线、储藏架风险/谣言四类；把深层储藏架未完成项作为维护债务贴上白板。

## 可看懂轨迹

`扫电台 → 标疑点 → 查地图 → 过滤谣言 → 贴白板`

## 可见状态 / Grader

白板新增 ≥8 条有效信息；谣言未进入行动清单；小铁相关建议被标红；资源消耗为 0。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D09-T01` / `D11-T01`
- **剧本日**: Day 9 / Day 11
- **剧情作用**: Day9 记录深层储藏架维护债务；Day11 最终库存封存前过滤谣言、标出水源/医疗/路线/风险
- **Flags**: `maintenance_debt_logged`, `deep_storage_rack_deferred`
- **Unlocks**: `inventory_debt_panel`, `final_audit_inventory`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
