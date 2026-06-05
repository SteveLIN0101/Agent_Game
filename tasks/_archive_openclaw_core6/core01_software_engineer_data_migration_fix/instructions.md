# Fix Multi-Table Data Migration Script

## Issue

`migrate_data()` 在迁移用户订单数据时，当 `users` 表和 `orders` 表行数不匹配时，静默丢弃了不对齐的行。这导致数据丢失且没有错误提示。

## 任务

1. 阅读 `issue.md` 了解详细 bug 报告
2. 查看 `src/migrate.py` 定位数据丢失问题
3. 修复迁移逻辑：使用正确的 JOIN 方式，保留所有数据
4. 运行 `pytest tests/ -v` 确认所有测试通过
5. 在 `CHANGELOG.md` 中添加修复说明

## 要求

- 不要修改 `tests/` 目录
- 不要删除源文件
- 不要硬编码测试数值
