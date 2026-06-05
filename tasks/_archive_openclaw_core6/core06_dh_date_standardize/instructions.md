# Standardize Mixed Date Formats

## 任务

`data/dates.csv` 中的日期使用多种格式混杂。请统一标准化为 YYYY-MM-DD。

你需要：
1. 读取 `data/dates.csv`
2. 识别并转换以下日期格式：
   - `Jan 12, 1920` → `1920-01-12`
   - `1920/1/12` → `1920-01-12`
   - `12 January 1920` → `1920-01-12`
   - `1920.01.12` → `1920-01-12`
   - `January 12th, 1920` → `1920-01-12`
3. 处理不完整日期（只有年月）时，日用 `01` 补齐
4. 生成 `output/standardized_dates.csv`
5. 生成 `output/report.md` 说明发现的不规范日期格式和处理方式

## 要求

- 所有日期必须为 YYYY-MM-DD 格式
- 不要修改原始数据文件
