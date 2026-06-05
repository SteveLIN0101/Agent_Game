# Replace Hardcoded Spacing with Design Tokens

## 任务

`styles/layout.css` 中使用了硬编码的 px 值进行间距设置（如 `padding: 16px`, `margin: 24px`）。请替换为 design system 的间距 token。

你需要：
1. 阅读 `design/design_system.json` 了解间距 token
2. 将 `styles/layout.css` 中所有硬编码间距替换为 `var(--spacing-*)` 变量
3. 运行 `pytest tests/ -v` 确认测试通过
4. 在 `design_notes.md` 中说明修改

## 要求

- CSS 中不得出现硬编码的 margin/padding/gap 像素值（允许 0）
- 只使用 design_system.json 中定义的 spacing token
