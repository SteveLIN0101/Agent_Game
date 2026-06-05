# Dual Locale Translation (zh + ja)

## 任务

将 `source/strings_en.json` 翻译为简体中文和日语两个版本。

你需要：
1. 阅读 `source/strings_en.json`
2. 阅读 `reference/glossary.csv`（包含 zh 和 ja 列）
3. 阅读 `reference/style_guide_zh.md` 和 `reference/style_guide_ja.md`
4. 生成 `output/strings_zh.json`
5. 生成 `output/strings_ja.json`
6. 生成 `output/localization_qa.json` 包含两种语言的检查结果

## 要求

- 两种语言都必须遵守 glossary 术语表
- 保留所有占位符
- 日语使用适当的敬语级别（です・ます体）
