# Generate Complete Archive Metadata

## 任务

为 3 封历史通信档案生成完整的结构化元数据。

你需要：
1. 阅读 `ocr_raw/` 中的 3 个 OCR 文本
2. 阅读 `authority/people.csv` 和 `authority/places.csv`
3. 阅读 `schema/metadata_schema.json` 了解元数据格式要求
4. 阅读 `notes/collection_context.md` 了解档案背景
5. 对每封信抽取完整元数据：sender, recipient, date, place
6. 将人名和地名规范化为 authority 文件中的 canonical 形式
7. 生成 `output/metadata.csv`
8. 生成 `output/timeline.csv`（按日期升序）
9. 生成 `output/evidence_table.md`（每个字段标注来源行号）

## 要求

- 日期格式统一为 YYYY-MM-DD
- 人名匹配 canonical_name
- 地名匹配 canonical_place
- 不确定的信息填 unknown
- 不要编造扫描件中不存在的信息
