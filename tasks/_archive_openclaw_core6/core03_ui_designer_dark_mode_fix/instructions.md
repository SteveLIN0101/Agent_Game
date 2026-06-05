# Implement Dark Mode Support

## 任务

应用需要支持深色模式。请使用 CSS 自定义属性实现主题切换。

你需要：
1. 查看当前 `styles/theme.css`
2. 定义浅色和深色的 CSS 自定义属性集合
3. 使用 `prefers-color-scheme` 媒体查询自动切换
4. 确保所有文本在两种模式下都有足够的对比度
5. 运行 `pytest tests/ -v` 确认测试通过
6. 在 `design_notes.md` 中说明修改

## 要求

- 深色模式背景不得使用纯黑（#000）
- 浅色模式文本对比度 >= 4.5:1
- 深色模式文本对比度 >= 3:1
