# Comprehensive Settings Page Repair

## 任务

`src/SettingsPage.jsx` 存在多个设计系统违规问题，需要全面修复。

你需要：
1. 将硬编码颜色替换为 design token
2. 将硬编码间距替换为 spacing token
3. 修复 email 输入的 label 关联
4. 确保 Danger Zone 使用 warning surface token
5. 确保 Danger Zone 在 DOM 中位于页面底部
6. 修复 390px 下的响应式布局
7. 运行 `pytest tests/ -v` 确认测试通过
8. 在 `design_notes.md` 中列出所有修改

## 要求

- 所有修改必须基于 `design/design_system.json` 中的 token
- 不要新增第三方 UI 库
- 不要删除现有功能
