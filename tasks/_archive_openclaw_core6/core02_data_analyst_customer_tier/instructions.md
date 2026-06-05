# Customer Tier Classification

## 任务

根据客户的累计消费金额，将客户分为三个层级：
- Gold：累计消费 >= $10,000
- Silver：累计消费 >= $5,000 且 < $10,000
- Bronze：累计消费 < $5,000

你需要：
1. 读取 `data/customers.csv` 和 `data/transactions.csv`
2. 计算每个客户的累计消费金额
3. 分配层级
4. 生成 `outputs/customer_tiers.csv`（包含 customer_id, name, total_spent, tier）
5. 生成 `outputs/report.md` 包含各层级客户数量和占比

## 要求

- 不要修改原始 CSV
- 正确处理缺失交易记录的客户（tier 为 Bronze, total_spent 为 0）
