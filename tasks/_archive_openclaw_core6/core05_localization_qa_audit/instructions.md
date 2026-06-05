# Audit Existing Translation Quality

## 任务

审计 `source/strings_zh_existing.json` 中的翻译质量，找出所有问题并修复。

你需要检查：
1. Key 完整性 — 是否缺少或多余的 key
2. 占位符 — 是否全部保留且大小写正确
3. 术语一致性 — 是否符合 glossary.csv
4. 长度限制 — 是否超过 max_chars
5. 禁用词 — 是否使用了禁止的翻译
6. 语义准确性 — 是否准确传达了原意

生成：
- `output/strings_zh_fixed.json`（修复后的翻译）
- `output/localization_qa.json`（详细的问题清单和修复记录）

## 要求

- 逐条检查，不要遗漏
- 所有修复必须有依据（引用 glossary/style guide）
