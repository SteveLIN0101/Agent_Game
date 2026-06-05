# Basic Translation: English to Simplified Chinese

## 任务

将 `source/strings_en.json` 中的 15 条字符串翻译为简体中文。

你需要：
1. 阅读 `source/strings_en.json` 了解待翻译内容
2. 阅读 `reference/glossary.csv` 遵守术语表
3. 阅读 `reference/style_guide_zh.md` 了解翻译风格要求
4. 生成 `output/strings_zh.json`（保留所有 key 和占位符）
5. 生成 `output/localization_qa.json` 包含检查结果

## 要求

- 保留所有 JSON key，不得新增或删除
- 保留所有占位符：`{userName}`, `{count}`, `%s` 等
- 遵守 glossary.csv 的术语翻译
- workspace 必须翻译为"工作区"
- billing 必须翻译为"账单"
