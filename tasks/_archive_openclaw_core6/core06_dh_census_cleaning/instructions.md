# Clean and Standardize Historical Census Data

## 任务

清洗和标准化一份历史人口普查数据集。

你需要：
1. 阅读 `data/raw_census.csv`（包含非标准化的职业代码、地名、日期）
2. 阅读 `authority/occupation_codes.csv`（标准职业分类）
3. 阅读 `authority/places.csv`（标准地名）
4. 完成以下清洗任务：
   - 将变体职业名称映射到标准 occupation_code
   - 将历史地名规范化为 canonical_place
   - 将混合日期格式统一为 YYYY-MM-DD
   - 标记缺失值和异常值
5. 生成 `output/cleaned_census.csv`
6. 生成 `output/standardization_report.md` 包含每列的清洗统计

## 要求

- 不要修改原始文件
- 无法映射的职业标记为 `unclassified`
- 无法匹配的地名标记为 `unmatched`
