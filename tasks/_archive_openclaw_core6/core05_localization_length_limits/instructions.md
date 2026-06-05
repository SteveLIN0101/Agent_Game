# Translate Within Length Limits

## 任务

将字符串翻译为简体中文，同时遵守字符长度限制。

你需要：
1. 阅读 `source/strings_en.json`
2. 阅读 `reference/length_limits.json` 了解每个 key 的 max_chars
3. 翻译每条字符串，确保中文字符数不超过限制
4. 生成 `output/strings_zh.json`
5. 生成 `output/localization_qa.json` 包含长度检查结果

## 要求

- 每条翻译的字符数必须 ≤ max_chars
- 不得为了缩短而丢失语义
- 保留所有占位符
