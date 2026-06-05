# Update Configuration Reference Documentation

## 任务

`docs/config_reference.md` 缺少新增的配置项文档。请更新。

你需要：
1. 阅读 `src/config.py` 了解所有配置项
2. 更新 `docs/config_reference.md` 添加：
   - `log_level` — 默认 `INFO`，可选 `DEBUG`, `INFO`, `WARNING`, `ERROR`
   - `cache_ttl` — 默认 `3600` 秒
   - `max_retries` — 默认 `3`
3. 每个配置项包含：名称、类型、默认值、说明
4. 运行 `pytest tests/ -v` 确认测试通过

## 要求

- 所有信息必须来自源代码
- 不要编造配置项
