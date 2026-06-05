# Generate Subscription Business Weekly Report

## 任务

根据 `data/` 下的四个 CSV 文件，生成 2025-W32 的订阅业务周报。

你需要：
1. 阅读 `docs/metric_definitions.md` 了解指标定义
2. 阅读 `docs/known_data_issues.md` 了解已知数据问题
3. 清洗重复的 payment 记录（保留最新的）
4. 计算以下指标：
   - MRR（月度经常性收入）
   - new_mrr（新增 MRR）
   - churned_mrr（流失 MRR）
   - net_mrr_growth（净 MRR 增长）
5. 找出 churned_mrr 最高的前三个 customer_segment
6. 生成 `outputs/summary.json`（包含所有指标）
7. 生成 `outputs/report.md`（包含分析方法说明）
8. 生成 `outputs/cleaned_payments.csv`（去重后的数据）

## 要求

- 不要修改 `data/` 目录中的原始 CSV
- 金额允许 ±0.01 误差
- report.md 必须包含数据清洗说明
