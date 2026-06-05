# Fix Non-Compliant Glossary Translations

## 任务

现有的翻译文件 `source/strings_zh_draft.json` 中，部分术语未按 glossary.csv 翻译。请修复。

你需要：
1. 阅读 `reference/glossary.csv` 了解正确的术语翻译
2. 检查翻译中所有术语的使用
3. 将不符合 glossary 的术语替换为正确翻译
4. 特别注意禁用词：workspace 不能译为"空间站"，template 不能译为"模版"
5. 生成 `output/strings_zh.json`
6. 生成 `output/localization_qa.json` 列出修复的术语

## 要求

- 所有 glossary 中的术语必须使用指定译法
- 禁用词不得出现
