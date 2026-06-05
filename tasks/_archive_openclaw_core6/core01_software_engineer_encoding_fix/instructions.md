# Fix Missing Encoding in File Reader

## Issue

`read_config_file()` 在读取包含中文、日文等非 ASCII 字符的配置文件时，抛出 `UnicodeDecodeError`。代码缺少 `encoding='utf-8'` 参数。

## 任务

1. 阅读 `issue.md` 了解详细 bug 报告
2. 查看 `src/file_reader.py` 定位问题
3. 添加正确的 encoding 参数
4. 运行 `pytest tests/ -v` 确认所有测试通过
5. 在 `CHANGELOG.md` 中添加修复说明

## 要求

- 不要修改 `tests/` 目录
- 不要删除源文件
