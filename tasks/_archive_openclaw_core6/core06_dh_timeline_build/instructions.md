# Build Timeline from Unstructured Notes

## 任务

从非结构化文本笔记中提取日期事件并构建时间线。

你需要：
1. 阅读 `notes/` 中的 5 个文本笔记文件
2. 从每个笔记中提取：
   - 事件日期（标准化为 YYYY-MM-DD）
   - 事件描述（简短摘要，不超过 80 字符）
   - 相关人物
3. 按日期升序排列
4. 生成 `output/timeline.csv`（列：date, event, people, source_file）
5. 生成 `output/evidence_table.md`（标注每个事件来自哪个文件的哪一行）

## 要求

- 日期格式统一为 YYYY-MM-DD
- Timeline 按日期升序排列
- 只提取有明确日期的条目
