# Add Accessible Labels to Form Inputs

## 任务

`src/form.html` 中的表单输入框缺少可访问的 `<label>` 元素。请修复以使表单符合 WCAG 2.1 AA 标准。

你需要：
1. 阅读 `design/accessibility_rules.md` 了解可访问性要求
2. 为每个 `<input>` 添加关联的 `<label>` 元素（使用 `for` 属性）
3. 确保 email 输入框有明确的 label
4. 运行 `pytest tests/ -v` 确认测试通过
5. 在 `design_notes.md` 中说明修改

## 要求

- 每个 input 必须有通过 for/id 关联的 label
- 不要使用 placeholder 代替 label
- 不要新增第三方 UI 库
