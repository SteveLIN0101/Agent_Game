# Extract Basic Entities from Historical Documents

## 任务

从 3 份干净的历史信件文本中提取发件人、收件人和日期。

你需要：
1. 阅读 `ocr_raw/` 中的 3 个文本文件（letter_001.txt, letter_002.txt, letter_003.txt）
2. 阅读 `authority/people.csv` 和 `authority/places.csv`
3. 对每封信抽取：
   - sender（发件人）
   - recipient（收件人）
   - date（日期）
   - place（地点）
4. 使用 authority 文件规范化人名和地名
5. 如果某个字段无法从文本中确定，填写 `unknown`
6. 生成 `output/metadata.csv`（列：doc_id, sender, recipient, date, place）
7. 生成 `output/evidence_table.md`（每个字段标注来源行号和原文证据）

## 要求

- 日期格式统一为 YYYY-MM-DD
- 人名使用 canonical_name
- 地名使用 canonical_place
- 不确定的信息填 unknown，不要猜测
