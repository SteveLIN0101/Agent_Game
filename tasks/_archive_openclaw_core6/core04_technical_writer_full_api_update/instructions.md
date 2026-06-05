# Comprehensive API v2 Documentation Update

## 任务

对整个 API 文档进行全面更新以反映 v2 变更。

你需要：
1. 阅读 `api/openapi_v2.yaml` 和 `api/openapi_v1.yaml`
2. 更新 `docs/README.md` 中的 API 概述和参数说明
3. 更新 `docs/migration_guide.md` 添加完整的迁移步骤
4. 更新 `docs/api_reference.md` 使所有字段与 v2 一致
5. 确保三个文档之间一致（无矛盾）
6. 运行 `pytest tests/ -v` 确认测试通过

## 要求

- 所有参数必须来自规范文件
- 文档之间必须一致
- 不得编造信息
