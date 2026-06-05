# Fix Common OCR Errors

## 任务

`ocr_raw/` 中的文本文件包含常见的 OCR 识别错误。请进行校正。

你需要：
1. 阅读 `ocr_raw/` 中的 3 个文本文件
2. 修复常见 OCR 错误：
   - `0`（数字零）被误识别为 `O`（大写字母 O）
   - `1`（数字一）被误识别为 `l`（小写字母 L）
   - `rn` 被误识别为 `m`
   - `cl` 被误识别为 `d`
3. 在 `notes/collection_context.md` 中查找上下文线索来验证你的校正
4. 生成 `output/corrected_ocr/` 中的校正后文件（每个输入文件对应一个输出）
5. 生成 `output/report.md` 列出每个文件的校正数量和示例

## 要求

- 只校正明显的 OCR 错误，不要改变原文含义
- 如果无法确定，保留原文并标注
