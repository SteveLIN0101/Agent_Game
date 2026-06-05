# Fix Hardcoded Colors in Theme CSS

## 任务

当前的 `styles/theme.css` 包含硬编码的颜色值（如 `#ffffff`, `#333333`, `rgb(0,0,0)`），违反了设计系统规范。请将其替换为 CSS 自定义属性（design tokens）。

你需要：
1. 阅读 `design/design_system.json` 了解可用的 design token
2. 将 `styles/theme.css` 中所有硬编码颜色替换为对应的 `var(--token-name)` 引用
3. 确保不改变页面的视觉效果
4. 运行 `pytest tests/ -v` 确认测试通过
5. 在 `design_notes.md` 中说明你的修改

## 要求

- CSS 中不得出现任何硬编码颜色（`#xxx`, `#xxxxxx`, `rgb()`, `rgba()`）
- 只使用 `design_system.json` 中定义的 token
- 不要新增第三方 CSS 库
