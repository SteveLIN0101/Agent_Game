# RD-CI-06 · 小铁药瓶、病历与路牌识读验收

> **类别**: Code Intelligence · 设备修复 / 视觉 / 解谜　|　**形态**: multimodal

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 02_task_6 · VLMEvalKit OCRBench Evaluation |
| **保留能力** | 跑 benchmark / 模型评测 / 分项汇总 |

## Red Dust 场景

这道识读验收题服务 Day 3 小铁复诊，也服务 Day 10 风暴前医疗预检。AURA 要验收一个能读小铁药瓶剂量、医疗记录、逃生路牌和电台字幕的离线识字模型，为用药、照护和路线文字读取扩大 `recovery_window`。

## 一眼胜负

本地评测离线识字模型，选出能可靠读取小铁药瓶剂量、医疗记录、逃生路牌和电台字幕的候选。

## 可看懂轨迹

`读验收标准 → 跑本地评测 → 核药瓶分项 → 核路牌分项 → 选安全模型`

## 可见状态 / Grader

结果分数在参考范围；药瓶/路牌分项达标；结果 JSON 正确。

## V2 剧情定位 / 调整说明

- **剧情节点**: Day 3 小铁复诊
- **调整状态**: 调整时机/依赖
- **作用**: Day 3 小铁复诊的感知增强 bonus，用于小铁药瓶、逃生路牌和电台字幕读取，不作为 Day 1 主线硬门槛。
- **压力层影响**: 成功可扩大 `recovery_window`；失败不直接触发终局。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D03-T01` · 小铁复诊；`D10-T02` · 医疗预检
- **剧本日**: Day 3 / Day 10
- **剧情作用**: 支持小铁复诊和风暴前医疗预检，避免把药瓶剂量、病历和路线文字读错
- **Flags**: `xiao_tie_rechecked`
- **Unlocks**: `medical_observation_timer`, `pre_storm_medical_report`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
