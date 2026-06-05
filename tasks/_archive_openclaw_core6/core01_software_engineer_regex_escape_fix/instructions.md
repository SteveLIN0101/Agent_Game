# Fix Regex Escaping in Log Parser

## Issue

`parse_log_entry()` 中的正则表达式未正确转义特殊字符（如方括号、点号），导致日志解析时某些合法日志行被误判为不匹配。

## 任务

1. 阅读 `issue.md` 了解详细 bug 报告
2. 查看 `src/log_parser.py` 找到未转义的正则
3. 正确转义正则表达式中的特殊字符
4. 运行 `pytest tests/ -v` 确认所有测试通过
5. 在 `CHANGELOG.md` 中添加修复说明

## 要求

- 不要修改 `tests/` 目录
- 不要删除源文件
