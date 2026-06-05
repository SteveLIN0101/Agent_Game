# Fix API Returning Wrong HTTP Status Code

## Issue

`create_resource()` API 在成功创建资源后返回 `200 OK`，但根据 REST 规范应返回 `201 Created`。客户端依赖正确的状态码来判断资源是否为新创建。

## 任务

1. 阅读 `issue.md` 了解详细 bug 报告
2. 查看 `src/api_handler.py` 修改返回的状态码
3. 确保响应体包含新创建资源的 location header
4. 运行 `pytest tests/ -v` 确认所有测试通过
5. 在 `CHANGELOG.md` 中添加修复说明

## 要求

- 不要修改 `tests/` 目录
- 不要删除源文件
