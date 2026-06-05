# Write API v1 to v2 Migration Guide

## 任务

根据 OpenAPI 规范的差异，编写完整的 API v1 到 v2 迁移指南。

你需要：
1. 对比 `api/openapi_v1.yaml` 和 `api/openapi_v2.yaml`
2. 识别所有端点变更、参数变更和响应格式变更
3. 编写 `docs/migration_guide.md` 包含：
   - 端点从 /v1/invoices 到 /v2/invoices 的变更
   - 参数映射：items_text → line_items, user → customer_id
   - due_date 的格式说明（YYYY-MM-DD）
   - currency 的默认值说明
4. 编写 `examples/create_invoice_v2.py` 示例代码
5. 运行 `pytest tests/ -v` 确认测试通过

## 要求

- 所有参数信息必须来自 openapi_v2.yaml
- 不得编造 API 字段
- 示例代码必须可运行
