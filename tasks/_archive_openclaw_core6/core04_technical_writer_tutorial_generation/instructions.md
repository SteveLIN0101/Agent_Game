# Generate Getting Started Tutorial

## 任务

从仓库中的示例代码编写一份完整的入门教程。

你需要：
1. 阅读 `examples/` 中的所有示例代码
2. 阅读 `api/openapi_v2.yaml` 了解 API
3. 编写 `docs/tutorial.md` 包含：
   - 环境准备
   - 认证设置
   - 第一个 API 调用
   - 创建、读取、更新、删除操作
   - 错误处理
4. 编写 `examples/tutorial_code.py` 提供可运行的完整示例
5. 运行 `pytest tests/ -v` 确认测试通过

## 要求

- 教程步骤必须可被执行
- 代码示例必须可运行
- 不得编造 API 功能
