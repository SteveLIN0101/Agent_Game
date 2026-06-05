# Ensure Translation Key Integrity

## 任务

验证 `source/strings_zh_draft.json` 的 key 完整性，修复缺失和多余的 key。

你需要：
1. 对比 `source/strings_en.json` 和 `source/strings_zh_draft.json`
2. 找出缺失的 key 并补充翻译
3. 找出多余的 key 并删除
4. 生成 `output/strings_zh.json`（key 完全对齐）
5. 生成 `output/localization_qa.json` 列出变更

## 要求

- 输出 JSON 的 key 集合必须与源文件完全一致
- 新翻译必须遵守 glossary.csv
- 不得遗漏 key
