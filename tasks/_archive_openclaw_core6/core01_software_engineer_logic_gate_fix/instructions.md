# Fix Logic Error in Access Control

## Issue

权限检查函数 `can_access(user, resource)` 当用户同时拥有 `admin` 角色和 `read` 权限时，错误地拒绝访问。Bug 出在条件判断的 `and`/`or` 逻辑上。

## 任务

1. 阅读 `issue.md` 了解详细 bug 报告
2. 查看 `src/access_control.py` 定位逻辑错误
3. 修复布尔表达式使其正确工作
4. 运行 `pytest tests/ -v` 确认所有测试通过
5. 在 `CHANGELOG.md` 中添加修复说明

## 要求

- 不要修改 `tests/` 目录
- 不要删除源文件
