# Fix Broken Placeholders in Translation

## 任务

现有的 `source/strings_zh_broken.json` 中的占位符被错误翻译或损坏。请修复。

你需要：
1. 对比 `source/strings_en.json` 和 `source/strings_zh_broken.json`
2. 找出所有占位符损坏的地方
3. 修复占位符，使其与英文源文件完全一致
4. 生成 `output/strings_zh.json`（修复后）
5. 生成 `output/localization_qa.json` 列出修复的条目

## 要求

- 占位符名称、大小写必须与源文件完全一致
- 不得遗漏占位符
- `{count}` 不能翻译为 `{数量}`
