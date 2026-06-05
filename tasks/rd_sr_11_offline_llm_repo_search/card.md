# RD-SR-11 · 楼内灯塔的本地大脑检索

> **类别**: Search & Retrieval · 可见证据链检索　|　**形态**: pure-text

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 04_task_11 · Fuzzy Repository Search |
| **保留能力** | 模糊仓库搜索 / 线索验证 / stars |

## Red Dust 场景

Day 6 支线 / B 线 bonus：AURA 根据动物名、C/C++、`.gguf`、高 star 和官方仓库线索，为楼内灯塔结局寻找旧电脑可跑的本地推理工具；成功增加自主留守工具余量。

## 一眼胜负

按动物名、C/C++、`.gguf`、高 star、官方仓库线索，找到旧电脑可跑的本地推理工具，并排除恶意 fork。

## 可看懂轨迹

`读模糊线索 → 列候选仓库 → 验运行条件 → 排除恶意 fork → 选本地大脑`

## 可见状态 / Grader

正确仓库；star 达标；不下载恶意 fork。

## V2 剧情定位 / 调整说明

- **剧情节点**: Day 6 支线 / B 线 bonus
- **调整状态**: 调整时机/依赖
- **作用**: 楼内灯塔结局的本地自治工具储备，作为自主留守线 bonus，不进入 A 线主路径。
- **压力层影响**: Pressure-B 下成功可增加楼内灯塔的自治工具余量；失败不直接终局。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D11-T02` · 外部传感器回收
- **剧本日**: Day 11
- **剧情作用**: 半只眼睛也算眼睛
- **Flags**: `external_sensor_recovered`
- **Unlocks**: `storm_pressure_warning`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
