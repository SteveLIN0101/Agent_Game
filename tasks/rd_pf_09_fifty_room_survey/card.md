# RD-PF-09 · 50 个房间普查

> **类别**: Productivity Flow · 避难所资料运营　|　**形态**: pure-text

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 01_task_9 · Crawl SCP-001 to SCP-050 with Text, Images, and Metadata |
| **保留能力** | 爬取 / 正文与图片提取 / JSONL 汇总 |

## Red Dust 场景

AURA 要普查 1-50 号房：门牌、危险等级、可见物资和隐藏可进入点。

## 一眼胜负

每个房间生成一张卡，观众能在地图上看到哪里危险、哪里有物资。

## 可看懂轨迹

`抓房间页 → 存正文 → 下图片 → 识别危险级 → 生成地图卡`

## 可见状态 / Grader

50 张房间卡完整；危险等级正确；无装饰图混入；隐藏入口计数正确。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D02-T04` · 同层楼道短探
- **剧本日**: Day 2
- **剧情作用**: 低风险获取路线与物资线索
- **Flags**: `same_floor_scout_available`
- **Unlocks**: `same_floor_partial_map`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
