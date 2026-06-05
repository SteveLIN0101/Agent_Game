# Add Visible Focus Indicators

## 任务

当前页面缺少可见的键盘焦点指示器，键盘用户无法知道当前聚焦在哪个元素。请添加 `:focus-visible` 样式。

你需要：
1. 查看 `styles/global.css`
2. 为所有可交互元素添加 `:focus-visible` 样式
3. Focus ring 必须有足够的对比度（至少 3:1）
4. 运行 `pytest tests/ -v` 确认测试通过
5. 在 `design_notes.md` 中说明修改

## 要求

- 不要移除默认的 `:focus` 样式
- 不要使用 `outline: none` 而不提供替代方案
