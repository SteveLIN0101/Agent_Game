# Transaction Anomaly Detection

## 任务

使用 IQR 方法识别交易数据中的异常值。

你需要：
1. 读取 `data/transactions.csv`
2. 计算交易金额的 Q1, Q3 和 IQR
3. 使用 1.5*IQR 规则识别异常值（outliers）
4. 生成 `outputs/anomalies.json` 包含：
   - Q1, Q3, IQR
   - lower_bound, upper_bound
   - 异常交易列表（transaction_id, amount, reason）
5. 生成 `outputs/report.md` 说明分析方法和发现

## 要求

- 不要修改原始 CSV
- 异常判断标准：amount < Q1 - 1.5*IQR 或 amount > Q3 + 1.5*IQR
