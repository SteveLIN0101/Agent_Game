# Add Inline Form Validation

## 任务

当前表单提交时不显示验证错误消息，用户不知道哪些字段有问题。请添加内联验证。

你需要：
1. 查看 `src/Form.jsx`
2. 为 email 字段添加格式验证
3. 为 required 字段添加非空验证
4. 在字段下方显示错误消息
5. 运行 `pytest tests/ -v` 确认测试通过
6. 在 `design_notes.md` 中说明修改

## 要求

- 错误消息必须有 `aria-live` 或 `role="alert"` 属性
- 验证在 blur 和 submit 时触发
