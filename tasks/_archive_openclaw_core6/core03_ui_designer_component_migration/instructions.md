# Migrate Components to Design System v2

## 任务

将 4 个组件从设计系统 v1 token 迁移到 v2 token。

你需要：
1. 阅读 `design/design_system_v2.json` 了解新的 token 命名
2. 迁移以下组件：
   - `src/Card.jsx` — 卡片容器
   - `src/Modal.jsx` — 模态对话框
   - `src/Badge.jsx` — 状态徽章
   - `src/Tooltip.jsx` — 工具提示
3. 更新所有 CSS 变量引用
4. 运行 `pytest tests/ -v` 确认测试通过
5. 在 `design_notes.md` 中列出每个组件的变更

## 要求

- 组件行为不得改变
- 不要引入 v1 和 v2 混用
