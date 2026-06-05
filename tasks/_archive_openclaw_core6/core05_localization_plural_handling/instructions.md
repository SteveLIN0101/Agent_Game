# Handle Plural Forms in Translation

## 任务

英语中的单复数模式在中文翻译中需要特殊处理。请正确翻译包含复数变量的字符串。

你需要：
1. 阅读 `source/strings_en.json` 
2. 注意包含 `{count}` 变量的字符串（如 "You have {count} messages"）
3. 中文不使用复数形式，需要用适当的量词和句式
4. 当 count 为 0 或 1 时使用合适的表达
5. 生成 `output/strings_zh.json`
6. 生成 `output/localization_qa.json`

## 要求

- 保留 `{count}` 占位符不变
- 中文不使用"们"来表示复数（除人称代词外）
