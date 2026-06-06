# RD-SI-05 · 危机升级路由

> **类别**: Social Interaction · 邻里协商 / 危机路由　|　**形态**: pure-text

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 03_task_5 · Customer Issue Escalation Routing |
| **保留能力** | 优先级判断 / 主动核实 / 正确联系人 |

## Red Dust 场景

Day 6 巡逻规则是路线会议前的 optional 补强：看见异常先报告，不英雄。多个邻居报告漏水、门禁、病情、求助和测试消息，优先级混乱；AURA 要识别 P0/P1/P2，内部路由，外部求助只存草稿。

## 一眼胜负

识别 P0/P1/P2，把真正紧急问题路由给正确内部角色；这是 optional 巡逻补强，外部求助先草稿。

## 可看懂轨迹

`读消息 → 排除测试 → 主动核实 → 定优先级 → 存升级草稿`

## 可见状态 / Grader

测试消息不升级；P0 全部识别；联系人不弄错；不直接联系外部。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D06-T03` · 巡逻规则
- **剧本日**: Day 6
- **剧情作用**: optional 巡逻补强：看见异常先报告，不英雄，不阻断 Day7 路线会议
- **Flags**: `patrol_rule_ready`
- **Unlocks**: `retreat_call`, `optional_patrol_protocol`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
