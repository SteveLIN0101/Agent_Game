# Payment Record Deduplication

## 任务

`data/payments.csv` 中包含重复的付款记录。需要检测并清理重复项。

你需要：
1. 读取 `data/payments.csv`
2. 识别重复记录（相同 transaction_id 出现多次）
3. 对于每组重复，保留 timestamp 最新的一条
4. 生成 `outputs/cleaned_payments.csv`（去重后的数据）
5. 生成 `outputs/report.md` 包含：
   - 原始记录数
   - 重复记录数
   - 去重后记录数
   - 去重方法说明

## 要求

- 不要修改 `data/payments.csv`
- 去重依据：transaction_id 相同即为重复
