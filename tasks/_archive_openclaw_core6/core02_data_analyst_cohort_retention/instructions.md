# User Cohort Retention Analysis

## 任务

从用户注册和活动日志中计算用户留存率。

你需要：
1. 读取 `data/user_registrations.csv`（user_id, signup_date）
2. 读取 `data/user_activity.csv`（user_id, activity_date）
3. 定义周队列（按 signup_date 所在周分组）
4. 计算每个队列的：
   - Day 1 留存率
   - Day 7 留存率
   - Day 30 留存率
5. 生成 `outputs/retention.json` 包含每队列的留存数据
6. 生成 `outputs/report.md` 包含留存分析

## 要求

- 不要修改原始 CSV
- 留存率以百分比表示（0-100，保留 1 位小数）
