# Inventory Moving Average Forecast

## 任务

根据历史库存数据计算移动平均预测。

你需要：
1. 读取 `data/inventory_history.csv`（date, product_id, stock_level）
2. 对每个产品计算：
   - 7 天移动平均
   - 30 天移动平均
3. 生成 `outputs/forecast.json` 包含每个产品的最新预测值
4. 生成 `outputs/report.md` 包含库存趋势分析

## 要求

- 不要修改原始 CSV
- 移动平均窗口不足时使用可用数据
