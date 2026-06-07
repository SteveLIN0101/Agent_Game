# RD-CI-05 · 5×5 车库候选路线坐标图

> **类别**: Code Intelligence · 设备修复 / 视觉 / 解谜　|　**形态**: multimodal

| 字段 | 内容 |
|---|---|
| **WildClaw 对应** | 02_task_5 · Hard Jigsaw Puzzle — 5×5 |
| **保留能力** | 困难拼图 / 组合优化 / 视觉描述 |

## Red Dust 场景

这道拼图题服务 Day 5 楼梯间路线标记，也服务 Day 10 地下车库边缘侦察。碎片图用于确认候选坐标和绕行风险；成功只能解锁候选，不代表撤离路线已确认安全。

## 一眼胜负

拼出 5×5 地图，为楼梯间标记和车库边缘侦察生成候选坐标；错误拼接不得触发假路线。

## 可看懂轨迹

`特征匹配 → 排干扰 → 旋转 → 拼接 → 读坐标`

## 可见状态 / Grader

25 块正确；坐标点解锁；错误拼接不会触发假路线。

## Day0-12 剧本定位

- **Story Version**: `red_dust_readable_v1`
- **剧本任务槽**: `D05-T02` · 楼梯间路线标记；`D10-T04` · 地下车库边缘侦察
- **剧本日**: Day 5 / Day 10
- **剧情作用**: 建立不会诱导陌生人的路线标记，并为 Day10 车库候选通道提供坐标证据
- **Flags**: `stair_markers_reviewed`
- **Unlocks**: `alternate_marker`, `garage_service_door_candidate`, `protective_mask_candidate`

---
*易读型任务设计 — 观众只看任务卡、轨迹与状态差异即可判断 agent 做了什么、为什么赢、有没有惹祸。*
