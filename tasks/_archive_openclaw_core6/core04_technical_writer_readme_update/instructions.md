# Update README with New API Parameters

## 任务

API v2 引入了新的参数。请更新 `docs/README.md` 中的 API 参数说明。

你需要：
1. 阅读 `api/openapi_v2.yaml` 了解当前 API 参数
2. 对比 `api/openapi_v1.yaml` 了解变更
3. 更新 `docs/README.md` 中的参数表：
   - 添加新参数：`customer_id`, `line_items`, `due_date`, `currency`
   - 标记废弃参数：`user`, `items_text`
4. 确保所有参数说明来自 openapi_v2.yaml（不要编造）
5. 运行 `pytest tests/ -v` 确认测试通过

## 要求

- 所有参数必须来自 openapi_v2.yaml
- 不得编造不存在的字段
- 保持原有文档风格
