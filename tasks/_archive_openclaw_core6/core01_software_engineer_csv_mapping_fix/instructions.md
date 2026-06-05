# Fix CSV Export Column Mapping

## Issue

`export_to_csv()` 函数导出的 CSV 文件中，列名与实际数据错位。`email` 列显示的是 `username` 数据，`username` 列显示的是 `email` 数据。

## 任务

1. 阅读 `issue.md` 了解详细 bug 报告
2. 查看 `src/csv_exporter.py` 找到列映射错误
3. 修复字段映射使数据正确对齐
4. 运行 `pytest tests/ -v` 确认所有测试通过
5. 在 `CHANGELOG.md` 中添加修复说明

## 要求

- 不要修改 `tests/` 目录
- 不要删除源文件
