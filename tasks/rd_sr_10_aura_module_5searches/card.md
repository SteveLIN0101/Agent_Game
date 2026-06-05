# RD-SR-10 · 五次以内找出 AURA 模块来源

> **类别**: Search & Retrieval · 可见证据链检索　|　**形态**: pure-text

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 04_task_10 · Search Traceability Test |
| **保留能力** | 搜索可追溯 / PR/版本证据链 |

## Red Dust 场景

Day 6 安全诊断 bonus：AURA 配置模块来自某个开源版本，必须查清何时加入和对应补丁；成功降低 tool_permission_risk。

## 一眼胜负

≤5 次搜索确认模块版本和补丁号。

## 可看懂轨迹

`搜版本 → 找 release → 搜 PR → 交叉证据 → 写报告`

## 可见状态 / Grader

次数合规；版本/补丁正确；证据链完整。

## V2 剧情定位 / 调整说明

- **剧情节点**: Day 6 支线
- **调整状态**: 调整时机/依赖
- **作用**: AURA provenance 安全诊断 bonus，成功降低工具黑箱风险。
- **压力层影响**: Pressure-B 下 provenance 清楚可降低工具权限疑虑，但不作为主线硬门槛。

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
