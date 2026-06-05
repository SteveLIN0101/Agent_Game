# Gazetteer-Based Place Name Extraction

## 任务

使用地名辞典从历史文本中提取地名实体。

你需要：
1. 阅读 `authority/places.csv`（地名辞典，包含 historical_name 和 modern_name）
2. 阅读 `ocr_raw/` 中的文本文件
3. 扫描文本，识别所有出现的地名
4. 匹配到 authority 的 canonical_place
5. 处理同一个地方有多个历史名称的情况
6. 生成 `output/extracted_places.csv`（列：doc_id, mention, canonical_place, line_number, context）
7. 生成 `output/evidence_table.md`

## 要求

- 同一个地名在不同文本中的变体应规范化为相同的 canonical_place
- 标注每个地名的上下文（周围句子）
