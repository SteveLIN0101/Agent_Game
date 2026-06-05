# Fix Syntax Errors in Example Code

## 任务

`examples/create_invoice.py` 中的示例代码包含语法错误，用户复制后无法运行。

你需要：
1. 阅读 `examples/create_invoice.py`
2. 修复所有语法错误使其可运行
3. 修复错误的 API 端点路径
4. 修复缺失的 import 语句
5. 确保示例使用当前 API v2 的参数
6. 运行 `pytest tests/ -v` 确认测试通过

## 要求

- 修复后的代码必须可以 `python3 examples/create_invoice.py` 运行
- 不能改变示例的语义
- 不要使用 v1 的 API 端点
