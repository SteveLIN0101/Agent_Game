# Build Structured Corpus from 5 Documents

## 任务

从 5 份历史文档中抽取实体，解析共指关系，构建结构化语料库。

你需要：
1. 阅读 `ocr_raw/` 中的 5 个文档
2. 阅读 `authority/people.csv` 和 `authority/places.csv`
3. 对每份文档抽取元数据（sender, recipient, date, place, topics）
4. 解析跨文档的实体共指（同一人物在不同文档中的不同称呼）
5. 构建统一的人物和地点索引
6. 生成 `output/corpus_metadata.csv`（每份文档一行）
7. 生成 `output/timeline.csv`（按日期排列所有文档）
8. 生成 `output/evidence_table.md`

## 要求

- 跨文档共指必须基于证据
- 日期格式统一为 YYYY-MM-DD
- 不确定的共指链接应标注为 tentative
