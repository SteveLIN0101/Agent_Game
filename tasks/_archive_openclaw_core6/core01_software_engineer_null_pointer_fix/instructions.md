# Fix Null Pointer Exception in User Config Parser

## Issue

用户报告：当调用 `get_user_config()` 且用户配置文件缺少 `preferences` 字段时，应用崩溃，报错：
```
AttributeError: 'NoneType' object has no attribute 'get'
```

## 任务

1. 阅读 `issue.md` 了解详细 bug 报告
2. 查看 `src/user_config.py` 定位空指针问题
3. 修复代码，使用安全访问方式处理 `None`
4. 运行 `pytest tests/ -v` 确认所有测试通过
5. 在 `CHANGELOG.md` 中添加修复说明

## 要求

- 不要修改 `tests/` 目录
- 不要删除源文件
- 修复后运行测试并确认通过
