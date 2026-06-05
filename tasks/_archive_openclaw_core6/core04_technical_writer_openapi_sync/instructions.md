# Sync OpenAPI Changes to Markdown Reference

## 任务

`docs/api_reference.md` 与 `api/openapi_v2.yaml` 不一致，请同步更新。

你需要：
1. 对比 `api/openapi_v2.yaml` 和 `docs/api_reference.md`
2. 更新文档中过时的字段说明
3. 添加缺失的端点和参数文档
4. 确保所有字段与 OpenAPI 规范一致
5. 运行 `pytest tests/ -v` 确认测试通过

## 要求

- 不得编造字段
- 保持文档结构清晰
