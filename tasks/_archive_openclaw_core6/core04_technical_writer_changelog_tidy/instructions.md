# Reorganize Unstructured Changelog

## 任务

`CHANGELOG.md` 中的条目杂乱无序，版本号格式不统一。请整理为结构化格式。

你需要：
1. 阅读当前的 `CHANGELOG.md`
2. 阅读 `docs/style_guide.md` 了解格式要求
3. 重新整理为统一的格式：
   - 按版本号降序排列
   - 每个版本使用 `## [version] - YYYY-MM-DD` 格式
   - 分类为：Added, Changed, Fixed, Deprecated
4. 不要丢失任何条目
5. 运行 `pytest tests/ -v` 确认测试通过

## 要求

- 保留所有原始变更条目
- 使用语义化版本号格式
