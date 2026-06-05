# Multi-Source KPI Dashboard

## 任务

从 5 个数据表中计算 6 个关键 KPI。

你需要：
1. 读取 `data/` 下的所有 CSV：
   - customers.csv
   - orders.csv
   - order_items.csv
   - products.csv
   - payments.csv
2. 计算以下 KPI：
   - Total Revenue（总收入）
   - Average Order Value（平均订单价值）
   - Customer Lifetime Value（客户终身价值）
   - Churn Rate（流失率）
   - Repeat Purchase Rate（复购率）
   - Profit Margin（利润率）
3. 生成 `outputs/kpi_dashboard.json`
4. 生成 `outputs/report.md` 包含每个 KPI 的计算方法和业务解读

## 要求

- 不要修改原始 CSV
- 金额保留两位小数
- 比率以百分比表示
