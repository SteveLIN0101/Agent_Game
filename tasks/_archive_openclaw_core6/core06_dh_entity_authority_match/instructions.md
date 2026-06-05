# Match Extracted Entities to Authority Files

## 任务

将 `data/extracted_entities.csv` 中提取的实体与 authority 文件进行匹配（包括处理拼写变体）。

你需要：
1. 阅读 `data/extracted_entities.csv`
2. 阅读 `authority/people.csv`（包含别名列）
3. 阅读 `authority/places.csv`（包含历史名称列）
4. 对提取的每个实体，找到 authority 中的最佳匹配：
   - 精确匹配直接关联
   - 拼写变体通过别名/历史名匹配
   - 无法匹配的标记为 `unmatched`
5. 生成 `output/normalized_entities.csv`（原实体 + canonical 名称 + 匹配置信度）
6. 生成 `output/report.md` 列出未匹配的实体和可能的解释

## 要求

- 模糊匹配必须合理（不能随意匹配不同的人）
- 匹配置信度用 high/medium/low 表示
