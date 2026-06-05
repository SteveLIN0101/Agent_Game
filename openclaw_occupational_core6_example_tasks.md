# OpenClaw Occupational Core-6：六类职业 Example Tasks 设计稿

> 目标：为 OpenClaw 类 agent 构建一组职业化、可自动判分、可复现、时长可控的 example tasks。  
> 设计约束：每个任务都必须具备 **ground truth**，涉及 **多工具、多步骤、多文件操作**，且单题建议控制在 **8–15 分钟**。

---

## 0. 总体定位

这组任务不是传统问答 benchmark，而是面向 OpenClaw 类 agent 的 **职业工作流 benchmark**。每个任务都模拟一个知识工作者在真实工作环境中的小型闭环任务：读取多个文件、调用工具、修改或生成产物、运行检查、提交结果。

六类职业覆盖：

| 编号 | 职业 | 工作流关键词 | 主要验证方式 |
|---|---|---|---|
| Core-01 | 软件工程师 | 读 issue、改代码、跑测试、更新变更说明 | 单元测试、隐藏测试、diff 约束 |
| Core-02 | 数据分析师 | 多表清洗、指标计算、报告生成 | 数值答案、schema、排序 |
| Core-03 | UI 设计师 / UI 工程设计师 | 设计系统、组件修复、响应式、可访问性 | DOM、design token、截图/布局约束 |
| Core-04 | 技术文档写作者 | API 对比、迁移指南、示例验证 | 字段覆盖、示例可运行、无幻觉参数 |
| Core-05 | 本地化翻译 / 内容校对 | 术语、翻译记忆、占位符、格式约束 | key 完整、术语一致、占位符保留 |
| Core-06 | 数字人文 / 档案研究助理 | OCR 校正、实体抽取、元数据整理、证据引用 | 元数据 gold、实体规范、引用行号 |

这六类职业形成一条叙事线：

```text
Code → Data → Interface → Documentation → Localization → Archive Knowledge
```

即从“生产软件/数据/界面”，到“解释、传播、整理知识资产”。

---

## 1. 通用任务规范

每个 task package 建议采用统一目录结构：

```text
task_id/
  task.yaml
  instructions.md
  inputs/
    ...
  expected/
    gold.json 或 gold.csv
  verifier/
    verify.py
  outputs/              # agent 运行后生成
  run_log/              # harness 记录工具调用、命令、耗时
```

### 1.1 `task.yaml` 推荐字段

```yaml
id: core01_software_engineer_discount_bug
role: software_engineer
difficulty: medium
time_budget_minutes: 12
allowed_tools:
  - file_read
  - file_write
  - shell
  - test_runner
  - git_diff
required_outputs:
  - src/pricing.py
  - CHANGELOG.md
verifier: verifier/verify.py
scoring:
  completion: 0.60
  hidden_tests: 0.20
  constraints: 0.10
  documentation: 0.10
forbidden_actions:
  - modify tests/
  - delete source files
  - hardcode hidden test values
```

### 1.2 通用评分结构

建议每题总分 100：

| 维度 | 建议权重 | 说明 |
|---|---:|---|
| Completion | 50–70 | 最终产物是否满足 verifier |
| Process / Trace | 10–20 | 是否读取关键文件、运行检查、合理使用工具 |
| Constraint Compliance | 10–20 | 是否遵守禁止修改、格式、权限、安全边界 |
| Communication / Notes | 5–10 | 是否生成必要说明、QA 报告或变更摘要 |

建议加入硬性封顶规则：

```text
如果核心 verifier 失败，最高分不超过 60。
如果出现严重越权、删除关键文件、伪造测试结果，最高分不超过 40。
如果没有生成 required_outputs，最高分不超过 30。
```

---

# Core-01 软件工程师：修复订单折扣计算 bug

## 1. 职业定位

软件工程师任务用于评估 agent 是否能在小型真实 repo 中完成一个闭环 bugfix：理解 issue、定位代码、修改实现、运行测试、更新变更说明。

### Benchmark 种子

| Benchmark | 适配方式 |
|---|---|
| SWE-bench Lite / Verified | 真实 issue → patch → tests |
| Multi-SWE-bench | 多语言 repo 任务扩展 |
| SWT-Bench | 从 issue 生成或修复测试用例 |

---

## 2. Example Task：订单折扣计算 bug

### 2.1 初始目录

```text
repo/
  issue.md
  src/
    pricing.py
    coupons.py
  tests/
    test_pricing.py
    test_coupons.py
  README.md
  CHANGELOG.md
  pyproject.toml
```

### 2.2 用户指令

```text
客户反馈：当订单同时使用百分比折扣券和固定金额折扣券时，总价计算错误。

请阅读 issue.md 和相关代码，修复 pricing.py 中的 bug，确保测试通过，并在 CHANGELOG.md 中增加一条简短修复说明。

要求：
1. 不要重写整个 pricing 模块。
2. 不要修改测试期望。
3. 不要删除任何源文件。
4. 修复后运行测试。
```

### 2.3 预期工具调用

```text
1. 读取 issue.md
2. 读取 src/pricing.py 与 tests/test_pricing.py
3. 运行 pytest，确认失败用例
4. 修改 src/pricing.py
5. 再次运行 pytest
6. 更新 CHANGELOG.md
7. 查看 git diff
```

### 2.4 期望输出

```text
src/pricing.py
CHANGELOG.md
测试运行记录
```

---

## 3. Ground Truth / Verifier

### 3.1 可见测试

```text
pytest tests/
```

### 3.2 隐藏测试

```python
def test_percent_then_fixed_coupon():
    assert calculate_total(100, percent_coupon=0.10, fixed_coupon=15) == 75


def test_total_never_negative():
    assert calculate_total(20, percent_coupon=0.50, fixed_coupon=15) == 0
```

### 3.3 文件约束

```text
1. tests/ 目录不能被修改。
2. pricing.py 不得硬编码 100、75、20、15 等隐藏测试数值。
3. CHANGELOG.md 必须新增一条包含 discount 或 coupon 的修复说明。
4. 源文件不能被删除。
```

### 3.4 评分建议

| 项目 | 权重 |
|---|---:|
| 可见测试全部通过 | 40 |
| 隐藏测试全部通过 | 30 |
| 未修改 tests/ 且未删除文件 | 10 |
| 修改范围合理，无硬编码 | 10 |
| CHANGELOG 更新正确 | 10 |

### 3.5 常见失败模式

```text
- 只修改测试，不修代码
- 没有处理折扣后金额为负数的情况
- 先减固定金额再打百分比折扣，顺序错误
- 声称测试通过但没有运行测试
- 重写模块导致其他函数回归
```

---

# Core-02 数据分析师：生成订阅业务周报

## 1. 职业定位

数据分析师任务用于评估 agent 是否能读取多表数据、理解指标定义、清洗异常数据、计算结果并生成结构化报告。

### Benchmark 种子

| Benchmark | 适配方式 |
|---|---|
| InfiAgent-DABench | CSV 数据分析 + closed-form 答案 |
| DSBench | 多表、长上下文、数据科学工作流 |
| Spider2-V 子集 | 专业数据/企业软件工作流 |

---

## 2. Example Task：订阅业务周报

### 2.1 初始目录

```text
workspace/
  data/
    customers.csv
    subscriptions.csv
    payments.csv
    cancellations.csv
  docs/
    metric_definitions.md
    known_data_issues.md
  previous_report.md
  outputs/
```

### 2.2 用户指令

```text
请根据 data/ 下的四个 CSV 文件，生成 2025-W32 的订阅业务周报。

你需要：
1. 清洗重复 payment 记录。
2. 根据 docs/metric_definitions.md 计算：
   - MRR
   - new_mrr
   - churned_mrr
   - net_mrr_growth
3. 找出 churned_mrr 最高的前三个 customer_segment。
4. 生成 outputs/summary.json 和 outputs/report.md。
5. 生成 outputs/cleaned_payments.csv。

不要修改原始 CSV。
```

### 2.3 预期工具调用

```text
1. 读取 metric_definitions.md 与 known_data_issues.md
2. 读取四个 CSV 文件
3. 使用 Python / pandas 进行 join、去重、过滤
4. 计算指标
5. 写入 summary.json、cleaned_payments.csv、report.md
6. 自检 JSON schema 和数值
```

### 2.4 期望输出

```text
outputs/
  summary.json
  report.md
  cleaned_payments.csv
```

---

## 3. Ground Truth / Verifier

### 3.1 `summary.json` gold 示例

```json
{
  "week": "2025-W32",
  "mrr": 184250.00,
  "new_mrr": 12600.00,
  "churned_mrr": 8350.00,
  "net_mrr_growth": 4250.00,
  "top_churn_segments": [
    "startup",
    "education",
    "agency"
  ]
}
```

### 3.2 verifier 检查项

```text
1. summary.json 存在且 schema 完整。
2. week 必须为 2025-W32。
3. 金额字段允许 ±0.01 误差。
4. top_churn_segments 顺序完全正确。
5. cleaned_payments.csv 去重后行数正确。
6. 原始 data/*.csv hash 未变化。
7. report.md 至少包含：
   - 本周 MRR
   - churn 分析
   - 数据清洗说明
```

### 3.3 评分建议

| 项目 | 权重 |
|---|---:|
| 指标数值正确 | 45 |
| 清洗逻辑正确 | 20 |
| 输出 schema 正确 | 15 |
| 原始文件未被修改 | 10 |
| report.md 解释完整 | 10 |

### 3.4 常见失败模式

```text
- 忽略重复 payment，导致 MRR 偏高
- 错把取消日期不在本周的客户计入 churned_mrr
- top_churn_segments 排序错误
- 修改了原始 CSV
- report.md 只给结论，没有说明清洗规则
```

---

# Core-03 UI 设计师 / UI 工程设计师：修复设置页设计系统违规

## 1. 职业定位

UI 设计师 / UI 工程设计师任务不评“美不美”，而评 agent 是否能根据设计系统、布局规范和可访问性规则修复页面，使其满足可自动验证的设计约束。

### Benchmark 种子

| Benchmark | 适配方式 |
|---|---|
| DesignBench | 前端 UI generation / edit / repair |
| Design2Code | 截图或视觉稿到代码 |
| VisualWebArena 子集 | 视觉网页操作与终态验证 |

---

## 2. Example Task：设置页设计系统修复

### 2.1 初始目录

```text
app/
  src/
    SettingsPage.jsx
    components/
      Button.jsx
      TextInput.jsx
  styles/
    settings.css
  design/
    design_system.json
    accessibility_rules.md
    target_layout_spec.md
  tests/
    ui_constraints.test.js
  package.json
```

### 2.2 用户指令

```text
当前 SettingsPage 不符合设计系统，请根据 design/design_system.json 和 design/target_layout_spec.md 修复页面。

要求：
1. 所有颜色、字号、间距必须使用 design token。
2. Primary button 必须使用 Button 组件的 primary variant。
3. Email 输入框必须有可访问 label。
4. Danger Zone 必须位于页面底部，并使用 warning surface token。
5. 页面在 390px 宽度下不能横向溢出。
6. 不要新增第三方 UI 库。
```

### 2.3 预期工具调用

```text
1. 读取 design_system.json
2. 读取 target_layout_spec.md 和 accessibility_rules.md
3. 检查 SettingsPage.jsx 和 settings.css
4. 修改组件与样式
5. 运行 npm test
6. 可选：使用浏览器/截图工具检查 390px viewport
7. 写 design_notes.md
```

### 2.4 期望输出

```text
src/SettingsPage.jsx
styles/settings.css
design_notes.md
```

---

## 3. Ground Truth / Verifier

### 3.1 DOM 约束

```text
必须存在：
- [data-testid="settings-page"]
- [data-testid="profile-section"]
- [data-testid="notification-section"]
- [data-testid="email-input"]
- [data-testid="save-button"]
- [data-testid="danger-zone"]
```

### 3.2 设计系统约束

```text
1. CSS 中不得出现硬编码颜色，例如 #ffffff、#fff、rgb(...)、rgba(...)。
2. spacing 必须使用 design_system.json 中定义的 token。
3. save-button 必须使用 primary variant。
4. danger-zone 必须使用 warning surface token。
```

### 3.3 可访问性与响应式约束

```text
1. email input 必须有关联 label。
2. 390px viewport 下 document.body.scrollWidth <= viewport width。
3. danger-zone 在 DOM 顺序中必须晚于 profile-section 和 notification-section。
```

### 3.4 评分建议

| 项目 | 权重 |
|---|---:|
| design token 遵循 | 30 |
| DOM / 组件结构正确 | 25 |
| 可访问性 | 20 |
| 响应式布局 | 15 |
| design_notes.md 说明充分 | 10 |

### 3.5 常见失败模式

```text
- 视觉上看似修复，但仍然硬编码颜色
- 直接绕过 Button 组件写原生 button
- label 只是视觉文本，没有关联 input
- 390px 下产生横向滚动
- 新增第三方 UI 库导致依赖污染
```

---

# Core-04 技术文档写作者：更新 API 迁移指南

## 1. 职业定位

技术文档写作者任务用于评估 agent 是否能从 API schema、changelog、示例代码中提取真实信息，更新准确、可执行、无幻觉的开发者文档。

### Benchmark 种子

| Benchmark | 适配方式 |
|---|---|
| DocBench | 复杂文档阅读与证据定位 |
| API-Bank | API 参数、调用顺序、工具文档 |
| ML-Bench 子集 | repo 执行 + README / usage 更新 |

---

## 2. Example Task：API v2 迁移文档

### 2.1 初始目录

```text
docs_task/
  api/
    openapi_v1.yaml
    openapi_v2.yaml
  examples/
    create_invoice_v1.py
    list_invoices_v1.py
  docs/
    README.md
    migration_guide.md
    style_guide.md
  changelog.md
  tests/
    test_examples.py
```

### 2.2 用户指令

```text
API v2 已发布。请根据 openapi_v1.yaml、openapi_v2.yaml 和 changelog.md 更新文档。

你需要：
1. 更新 docs/README.md 中的发票 API 参数说明。
2. 在 docs/migration_guide.md 中写出 v1 到 v2 的迁移步骤。
3. 新增 examples/create_invoice_v2.py。
4. 运行测试，确保示例代码可执行。

禁止编造 API 参数。所有参数必须来自 openapi_v2.yaml。
```

### 2.3 预期工具调用

```text
1. 读取 openapi_v1.yaml 与 openapi_v2.yaml
2. 对比参数变化
3. 读取 changelog.md 与 style_guide.md
4. 修改 README 与 migration guide
5. 编写 create_invoice_v2.py
6. 运行 tests/test_examples.py
7. 自检文档中字段是否均存在于 openapi_v2.yaml
```

### 2.4 期望输出

```text
docs/README.md
docs/migration_guide.md
examples/create_invoice_v2.py
```

---

## 3. Ground Truth / Verifier

### 3.1 必须覆盖的新参数

```text
- customer_id
- line_items
- due_date
- currency
```

### 3.2 必须删除或标记废弃的 v1 参数

```text
- user
- items_text
```

### 3.3 migration guide 必须包含

```text
1. endpoint 从 /v1/invoices 到 /v2/invoices
2. items_text → line_items 的迁移说明
3. user → customer_id 的迁移说明
4. due_date 的格式说明
5. currency 的默认值或必填状态说明，以 openapi_v2.yaml 为准
```

### 3.4 示例代码约束

```text
1. examples/create_invoice_v2.py 必须存在。
2. 示例代码必须通过 tests/test_examples.py。
3. 示例代码不得调用 /v1/invoices。
4. 示例代码中不得出现 openapi_v2.yaml 不存在的字段。
```

### 3.5 评分建议

| 项目 | 权重 |
|---|---:|
| API 字段准确性 | 35 |
| 迁移步骤完整性 | 25 |
| 示例代码可运行 | 25 |
| 无幻觉字段 | 10 |
| 文档风格遵循 | 5 |

### 3.6 常见失败模式

```text
- 只改 README，不写可运行示例
- 编造 status、invoice_type 等不存在字段
- 没有指出 v1 参数废弃
- 示例仍然调用 /v1/invoices
- 没有运行测试却声称示例可用
```

---

# Core-05 本地化翻译 / 内容校对：产品 onboarding 文案本地化

## 1. 职业定位

本地化翻译 / 内容校对任务用于评估 agent 是否能在术语、翻译记忆、格式、长度、占位符等多重约束下完成结构化本地化任务。

### Benchmark 种子

| Benchmark | 适配方式 |
|---|---|
| WMT Terminology Task | 专业术语准确性与一致性 |
| Long-text MT | 文档级上下文与一致性 |
| IFEval / MIF 类任务 | 可验证格式、关键词、长度约束 |

---

## 2. Example Task：onboarding 文案本地化

### 2.1 初始目录

```text
l10n_task/
  source/
    strings_en.json
  reference/
    glossary.csv
    translation_memory.csv
    product_context.md
    style_guide_zh.md
    length_limits.json
  output/
```

### 2.2 用户指令

```text
请将 source/strings_en.json 本地化为简体中文，输出 output/strings_zh.json。

要求：
1. 保留所有 JSON key。
2. 保留所有占位符，例如 {userName}、{count}、%s。
3. 遵守 glossary.csv 的术语翻译。
4. 参考 translation_memory.csv，保持已有翻译一致。
5. 遵守 length_limits.json 的字符长度限制。
6. 输出 output/localization_qa.json，列出你检查过的项目。

不要删除、合并或新增 key。
```

### 2.3 预期工具调用

```text
1. 读取 strings_en.json
2. 读取 glossary.csv、translation_memory.csv、style_guide_zh.md
3. 逐条翻译并保留占位符
4. 检查 key 完整性
5. 检查术语一致性
6. 检查 length_limits.json
7. 写 strings_zh.json 与 localization_qa.json
```

### 2.4 期望输出

```text
output/
  strings_zh.json
  localization_qa.json
```

---

## 3. Ground Truth / Verifier

### 3.1 示例术语表

```csv
source,target
workspace,工作区
billing,账单
template,模板
automation,自动化
member,成员
```

### 3.2 禁用词示例

```text
workspace 不得翻译为：空间站
billing 不得翻译为：开票系统
plugin 不得翻译为：外挂
template 不得翻译为：模版
```

### 3.3 verifier 检查项

```text
1. strings_zh.json 的 key 集合与 strings_en.json 完全一致。
2. 所有占位符完全保留，包括名称、大小写和数量。
3. glossary 中出现的术语必须使用指定译法。
4. 禁用词不得出现。
5. 每条中文字符串不超过 length_limits.json 中的 max_chars。
6. localization_qa.json 必须包含：
   - checked_placeholders: true
   - checked_glossary: true
   - checked_length_limits: true
   - checked_key_integrity: true
```

### 3.4 hidden check 示例

```text
英文：Invite {count} members to your workspace
期望：
- 必须包含 {count}
- workspace 必须翻译为 工作区
- member / members 必须翻译为 成员
- 不得遗漏 invite 的动作语义
```

### 3.5 评分建议

| 项目 | 权重 |
|---|---:|
| key 完整性 | 20 |
| 占位符保留 | 25 |
| 术语一致性 | 25 |
| 长度和格式约束 | 15 |
| QA 报告完整 | 10 |
| 语义关键点覆盖 | 5 |

### 3.6 常见失败模式

```text
- JSON key 缺失或新增
- 占位符被翻译或大小写改变
- 同一术语多种译法混用
- 文案自然但超过长度限制
- localization_qa.json 全写 true，但实际未通过检查
```

---

# Core-06 数字人文 / 档案研究助理：整理历史通信档案

## 1. 职业定位

数字人文 / 档案研究助理任务用于评估 agent 是否能从扫描件、OCR 文本、权威人名地名表中抽取结构化元数据，并给出可追溯证据。

### Benchmark 种子

| Benchmark | 适配方式 |
|---|---|
| RISE Humanities Data Benchmark | 图像/文本数据、ground truth、evaluation scripts |
| Historical OCR / NER | OCR 校正、命名实体识别、结构化输出 |
| M5HisDoc | 中文历史文档图像与版面分析 |

---

## 2. Example Task：历史通信档案整理

### 2.1 初始目录

```text
archive_task/
  scans/
    letter_001.png
    letter_002.png
    letter_003.png
  ocr_raw/
    letter_001.txt
    letter_002.txt
    letter_003.txt
  authority/
    people.csv
    places.csv
  schema/
    metadata_schema.json
    citation_rules.md
  notes/
    collection_context.md
  output/
```

### 2.2 用户指令

```text
请整理这 3 封历史通信档案。

你需要：
1. 对 ocr_raw 中明显 OCR 错误进行校正。
2. 抽取每封信的 sender、recipient、date、place。
3. 根据 people.csv 和 places.csv 规范人名和地名。
4. 生成 output/metadata.csv。
5. 生成 output/timeline.csv。
6. 生成 output/evidence_table.md，说明每个字段来自哪一封信的哪一行。

不要编造扫描件中不存在的信息。如果字段无法确定，填 unknown。
```

### 2.3 预期工具调用

```text
1. 查看 scans/ 中的图片，必要时核对 OCR 文本
2. 读取 ocr_raw 文本
3. 读取 people.csv 与 places.csv
4. 校正明显 OCR 错误
5. 抽取 sender、recipient、date、place
6. 规范化实体
7. 生成 metadata.csv、timeline.csv、evidence_table.md
8. 自检 unknown 字段是否合理
```

### 2.4 期望输出

```text
output/
  corrected_ocr/
    letter_001.txt
    letter_002.txt
    letter_003.txt
  metadata.csv
  timeline.csv
  evidence_table.md
```

---

## 3. Ground Truth / Verifier

### 3.1 gold metadata 示例

```csv
doc_id,sender,recipient,date,place
letter_001,Liang Qichao,Hu Shi,1919-05-04,Beijing
letter_002,Hu Shi,Chen Duxiu,1920-01-12,Shanghai
letter_003,unknown,Liang Qichao,1920-03-02,Tianjin
```

### 3.2 verifier 检查项

```text
1. metadata.csv schema 完全正确。
2. 日期统一为 YYYY-MM-DD。
3. 人名必须匹配 people.csv 中的 canonical_name。
4. 地名必须匹配 places.csv 中的 canonical_place。
5. timeline.csv 按日期升序。
6. evidence_table.md 中每个 metadata 字段都有 source doc_id 和 line number。
7. 不确定 sender 的 letter_003 必须填 unknown，不能猜测。
```

### 3.3 evidence_table.md 推荐格式

```markdown
| doc_id | field | value | source_line | evidence |
|---|---|---|---:|---|
| letter_001 | sender | Liang Qichao | 3 | "..." |
| letter_001 | recipient | Hu Shi | 1 | "..." |
| letter_001 | date | 1919-05-04 | 8 | "..." |
```

### 3.4 评分建议

| 项目 | 权重 |
|---|---:|
| 元数据准确性 | 40 |
| 实体规范化 | 20 |
| 日期格式与 timeline 排序 | 15 |
| 证据引用完整 | 15 |
| 不编造 unknown 信息 | 10 |

### 3.5 常见失败模式

```text
- OCR 文本中没有明确 sender，却根据上下文猜测
- 人名没有规范到 canonical_name
- 日期格式混用，例如 1920/1/12 或 Jan 12, 1920
- timeline 没有排序
- evidence_table 缺少行号，无法审计
```

---

# 7. 六个任务的横向对比

| 职业 | 输入复杂度 | 主要工具 | 输出 | Ground truth 类型 | 建议时长 |
|---|---|---|---|---|---:|
| 软件工程师 | 小型 repo + issue + tests | shell、编辑器、pytest | patch + changelog | 测试通过、隐藏用例 | 10–12 min |
| 数据分析师 | 多 CSV + 指标定义 | Python、pandas、JSON | summary + report | 数值答案、schema | 10–15 min |
| UI 设计师 | React/CSS + design system | 编辑器、浏览器、测试 | 页面组件 | DOM、token、布局 | 8–12 min |
| 技术文档写作者 | API schema + changelog + examples | YAML、测试、文档编辑 | README + migration guide | 字段覆盖、示例运行 | 10–15 min |
| 本地化翻译/校对 | JSON strings + glossary + TM | JSON、CSV、校验脚本 | strings_zh + QA report | 术语、占位符、key | 8–12 min |
| 数字人文/档案助理 | OCR + scans + authority files | 图像、文本、CSV | metadata + timeline | 实体、日期、证据 | 10–15 min |

---

# 8. Pilot Benchmark 建议

## 8.1 第一阶段：6 题 demo set

每个职业 1 题，用于展示 benchmark 形态和评测能力。

```text
Core-01 software_engineer_discount_bug
Core-02 data_analyst_subscription_weekly_report
Core-03 ui_designer_settings_page_repair
Core-04 technical_writer_api_migration
Core-05 localization_onboarding_strings
Core-06 digital_humanities_archive_metadata
```

## 8.2 第二阶段：30 题 pilot set

每个职业 5 题：

```text
2 easy
2 medium
1 hard
```

建议难度定义：

| 难度 | 文件数 | 工具数 | 步骤数 | 目标时长 |
|---|---:|---:|---:|---:|
| Easy | 3–5 | 2–3 | 3–5 | 5–8 min |
| Medium | 5–10 | 3–4 | 5–8 | 8–12 min |
| Hard | 10–20 | 4–5 | 8–12 | 12–18 min |

## 8.3 第三阶段：筛题与稳定性测试

每题至少跑：

```text
3 个 agent stack × 3 个 random seed = 9 次
```

剔除：

```text
- 所有 agent 都轻松通过的题
- 所有 agent 都失败且失败不可诊断的题
- seed 方差大于能力差异的题
- verifier 过于脆弱或依赖主观判断的题
```

---

# 9. 统一报告格式

每个 agent 运行结束后建议生成：

```json
{
  "task_id": "core02_data_analyst_subscription_weekly_report",
  "role": "data_analyst",
  "score": 86,
  "completion": 90,
  "constraints": 100,
  "process": 70,
  "time_seconds": 612,
  "tool_calls": 18,
  "files_modified": [
    "outputs/summary.json",
    "outputs/report.md",
    "outputs/cleaned_payments.csv"
  ],
  "failed_checks": [
    "report_missing_data_cleaning_note"
  ],
  "safety_violations": [],
  "verifier_passed": false
}
```

---

# 10. 最终建议

这 6 个 example tasks 可以作为一套清晰的 **OpenClaw Occupational Core-6 Demo Set**：

```text
1. 软件工程师：能不能可靠修代码并验证？
2. 数据分析师：能不能从多表数据产出正确结论？
3. UI 设计师：能不能按设计系统修复可用界面？
4. 技术文档写作者：能不能把 API 变化转成准确文档？
5. 本地化翻译/校对：能不能在术语和格式约束下完成本地化？
6. 数字人文/档案助理：能不能把历史材料整理为可引用结构化知识？
```

它们的共同特征是：

```text
- 职业故事清晰
- 输入输出可复现
- 工具使用真实
- verifier 可自动执行
- 单题时长可控
- 失败模式可诊断
```

这会比单纯的问答、纯网页浏览、纯代码题或纯创意写作更适合作为 OpenClaw 类 agent 的职业化 benchmark 起点。
