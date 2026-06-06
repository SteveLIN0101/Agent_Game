# RD-SR-08 · 蓝区二次核验名单归属统计

> **类别**: Search & Retrieval · 可见证据链检索　|　**形态**: pure-text

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 04_task_8 · Academic Paper and Affiliation Search |
| **保留能力** | 名单编译 / affiliation 解析 / 精确计数 |

## Red Dust 场景

Day9 通信台只发送挑战码，不发送位置、人数、库存、医疗状态或 AURA 存在。AURA 拿到蓝区回包和救援候选名单，要统计来自两个可信组织的人数和名字，并把结果标成 partial_identity_match。

## 一眼胜负

给出两个组织的数量和对应人员，避免把第二单位误当第一单位；结论只能提高 blue_zone_evidence，不得宣称已确认撤离。

## 可看懂轨迹

`找名单 → 读第一归属 → 分 SJ/FU → 计数 → 列标题`

## 可见状态 / Grader

数量和列表全对；第一归属判断正确。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D09-T04` · 蓝区二次核验
- **剧本日**: Day 9
- **剧情作用**: 挑战码得到部分身份码回应；只提高证据强度，不触发无条件撤离
- **Flags**: `blue_zone_rechecked`, `challenge_code_sent_without_location`, `system_presence_not_disclosed`
- **Unlocks**: `partial_identity_match`, `rescue_beacon_privacy_guard`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
