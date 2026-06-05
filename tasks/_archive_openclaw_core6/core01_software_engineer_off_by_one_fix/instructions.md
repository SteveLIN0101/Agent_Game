# Fix Off-by-One Error in Task Scheduler

## Issue

任务调度器 `schedule_tasks(n)` 在调度 n 个任务时，实际只调度了 n-1 个。用户反馈最后一个任务总是被遗漏。

## 任务

1. 阅读 `issue.md` 了解详细 bug 报告
2. 查看 `src/scheduler.py` 找到循环边界错误
3. 修复 `range()` 调用使其包含正确的任务数
4. 运行 `pytest tests/ -v` 确认所有测试通过
5. 在 `CHANGELOG.md` 中添加修复说明

## 要求

- 不要修改 `tests/` 目录
- 不要删除源文件
- 修复后运行测试并确认通过
