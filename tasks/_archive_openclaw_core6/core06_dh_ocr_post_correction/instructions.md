# Advanced OCR Post-Correction with Context Rules

## 任务

使用上下文规则对严重退化的 OCR 文本进行后校正。

你需要：
1. 阅读 `ocr_raw/` 中的 3 个严重退化的 OCR 文本
2. 阅读 `notes/collection_context.md` 了解文档背景
3. 应用以下校正策略：
   - 词典校正（根据 `reference/dictionary.txt` 中的历史词汇表）
   - 语法校正（修复明显的断句错误）
   - 上下文校正（根据上下文推断正确词汇）
4. 生成 `output/corrected_ocr/` 中的校正文件
5. 生成 `output/report.md` 说明校正策略和校正统计

## 要求

- 不要过度校正（不确定的地方保留原文）
- 在 report 中标注低置信度的校正
