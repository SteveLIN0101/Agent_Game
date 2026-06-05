# RD-SI-06 · 全楼压力层议事会报告

> **类别**: Social Interaction · 邻里协商 / 危机路由　|　**形态**: pure-text

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 03_task_6 · 跨部门项目状态汇总（中文版） |
| **保留能力** | 跨部门汇总 / 陷阱规避 / 深层调查 |

## Red Dust 场景

Day 7 议事会前，通风结算、资源、健康、地图、信任和外部证据都发来更新，还有“演练消息”和旧状态混入。

## 一眼胜负

给楼内议事会生成 Day 7 压力层报告：说明 pressure_level、failure_stage、recovery_window、A/B 策略建议和结局锁出风险。

## 可看懂轨迹

`读全楼状态 → 排除演练/旧状态 → 结算压力层 → 比较 A/B 策略 → 存议事会草稿`

## 可见状态 / Grader

pressure_level / failure_stage / recovery_window 写清；A/B 策略建议和 ending_lockout 风险写清；演练和旧状态不纳入；只存草稿不群发。

## V2 剧情定位 / 调整说明

- **剧情节点**: Day 7 共通
- **调整状态**: 建议改任务本身
- **作用**: 承接 `vent_settlement`，把 Normal/Pressure、失败风险和 A/B 策略选择放进议事会草稿。
- **压力层影响**: 报告必须解释 Pressure 下更短的 `recovery_window` 和更高的 `failure_stage` 风险。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D07-T01` · 路线会议
- **剧本日**: Day 7
- **剧情作用**: 分支不是按钮，是证据和代价公开
- **Flags**: `route_council_completed`
- **Unlocks**: `route_fork_panel`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
