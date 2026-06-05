# Fix Sort Comparator Returning Wrong Order

## Issue

`sort_by_date()` 函数在排序日期列表时返回相反的顺序。升序排序返回降序结果，反之亦然。问题出在比较器函数的返回值上。

## 任务

1. 阅读 `issue.md` 了解详细 bug 报告
2. 查看 `src/sort_utils.py` 定位比较器错误
3. 修复比较逻辑使排序顺序正确
4. 运行 `pytest tests/ -v` 确认所有测试通过
5. 在 `CHANGELOG.md` 中添加修复说明

## 要求

- 不要修改 `tests/` 目录
- 不要删除源文件
