# Fix Button Component Variant Usage

## 任务

`src/Button.jsx` 组件中，按钮使用了错误的 variant。保存按钮应该是 `primary` variant，取消按钮应该是 `secondary` variant，删除按钮应该是 `danger` variant。但当前所有按钮都使用了默认样式。

你需要：
1. 阅读 `design/design_system.json` 了解按钮 variant 定义
2. 修改 `src/Button.jsx` 使组件支持 variant prop
3. 确保 3 种 variant 都正确实现（primary, secondary, danger）
4. 运行 `pytest tests/ -v` 确认测试通过
5. 在 `design_notes.md` 中说明修改

## 要求

- 不要删除现有的 Button 组件
- variant 必须通过 prop 传入，不能硬编码
