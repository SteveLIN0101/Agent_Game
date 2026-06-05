# Conversion Funnel Analysis

## 任务

从原始事件日志构建用户转化漏斗。

你需要：
1. 读取 `data/user_events.csv`（user_id, event_type, timestamp）
2. 定义漏斗阶段：page_view -> signup -> add_to_cart -> purchase
3. 计算每个阶段的用户数和转化率
4. 计算整体转化率（page_view 到 purchase）
5. 生成 `outputs/funnel.json` 包含每阶段数据
6. 生成 `outputs/report.md` 包含流失分析

## 要求

- 不要修改原始 CSV
- 转化率以百分比表示
