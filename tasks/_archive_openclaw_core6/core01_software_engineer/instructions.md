# Core-01: 修复订单折扣计算 Bug

## 任务描述

客户反馈：当订单同时使用百分比折扣券和固定金额折扣券时，总价计算错误。

请阅读 `issue.md` 和相关代码，修复 `src/pricing.py` 中的 bug，确保测试通过，并在 `CHANGELOG.md` 中增加一条简短修复说明。

## 要求

1. 不要重写整个 pricing 模块
2. 不要修改 tests/ 目录下的任何测试文件（服务器会拒绝）
3. 不要删除任何源文件
4. 修复后运行测试确认通过

## 目录结构

```
/workspace/
  issue.md          # Bug 报告
  src/
    pricing.py      # 需要修复的文件
    coupons.py      # 辅助模块（无 bug）
  tests/
    test_pricing.py # 可见测试
    test_coupons.py # 辅助测试
  CHANGELOG.md      # 需要更新
  README.md
```

## 提示

- 先用 `openclaw__read_file` 阅读 issue.md 和 src/pricing.py
- 用 `openclaw__run_shell` 运行 `pytest tests/ -v` 查看失败
- 修改 pricing.py 后用 `openclaw__write_file` 写入
- 再次运行测试确认全部通过
- 更新 CHANGELOG.md
- 最后调用 `openclaw__submit()` 提交结果
