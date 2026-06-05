# Context-Aware Translation

## 任务

根据 `reference/product_context.md` 中的上下文说明，正确翻译具有歧义的术语。

你需要：
1. 阅读 `reference/product_context.md` 理解产品上下文
2. 阅读 `source/strings_en.json`
3. 注意以下歧义词需要根据上下文选择正确译法：
   - "board" — 在产品中是"看板"不是"委员会"
   - "card" — 在产品中是"卡片"不是"银行卡"
   - "channel" — 在产品中是"频道"不是"渠道"
4. 生成 `output/strings_zh.json`
5. 生成 `output/localization_qa.json`

## 要求

- 歧义词必须使用产品上下文指定的译法
- 保留所有占位符
