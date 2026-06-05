# Product Revenue Ranking

## 任务

根据销售数据，按收入对产品进行排名。正确处理销售额相同的产品（并列排名）。

你需要：
1. 读取 `data/products.csv` 和 `data/order_items.csv`
2. 计算每个产品的总收入（quantity * unit_price）
3. 按收入降序排名（使用 dense ranking 处理并列）
4. 生成 `outputs/product_ranking.csv`（包含 rank, product_id, product_name, total_revenue）
5. 生成 `outputs/report.md` 包含 Top 3 产品分析

## 要求

- 不要修改原始 CSV
- 排名必须使用 dense ranking（并列不跳号）
