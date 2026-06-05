# Progress — Agent Game Benchmark Design Discussion

> 进度追踪文件，记录每次讨论的议题和结论。

---

## 2026-05-16 · Session 1

### 已讨论
- [x] 建立 Memory.md 和 Progress.md
- [x] 写入工作准则（子代理网络检索）
- [x] Slide 02 双轴范式总览深度拆解（PROF-12 / AURA / SHELTER 三层架构）
- [x] 四 Gap 诊断框架确认 + 独立文档输出
- [x] 用户自行总结了 Gap 1（污染）和 Gap 2（标量崇拜），补充了 Gap 3（时间维度缺失）和 Gap 4（后果真空）

### 产出文件
- `docs/design-discussion/Four-Gaps-Analysis.md` — 四 Gap 完整分析

### 进行中
- [ ] 等待用户下一轮提问

### 待讨论
- PROF-12 从 6 职业扩展到 12 职业的设计路径
- SHELTER 30 天剧情引擎实现方案
- LongTermBenefitCorrelation 反事实估计算法
- 嫁接机制的工程实现细节
- 评分体系的 4 维加权设计

---

## 2026-05-31 · Red Dust 可读任务进展同步

### 已讨论
- [x] 明确 Codex 默认第一读取的项目记忆/指令入口是 `AGENTS.md`
- [x] 明确仓库自身的设计讨论代表记忆是 `docs/design-discussion/Memory.md`
- [x] 核对 `AGENTS.md`、`CLAUDE.md`、`red_dust_readable_task_conversion.html`、`tasks/RED_DUST_INDEX.md`
- [x] 确认默认 `tasks/` 已切换为 60 个 Red Dust readable tasks
- [x] 确认旧 Occupational Core-6 已归档到 `tasks/_archive_openclaw_core6/`
- [x] 确认 60 个 Red Dust 任务均已 runnable + auto-scored
- [x] 确认当前 grader 覆盖为 `37 family deep + 2 bespoke deep + 21 generic scaffold`
- [x] 验证 `openclaw agent --agent main -m hello` 可调用，并执行 `/clear` 清理上下文

### 产出文件
- `AGENTS.md` — 更新为 Codex-facing 当前事实源
- `CLAUDE.md` — 同步当前 Red Dust 状态
- `docs/design-discussion/Memory.md` — 从设计讨论旧状态更新为当前工程记忆
- `docs/design-discussion/Progress.md` — 追加本次进展记录

### 验证结果
- Red Dust focused tests:
  - `tests/test_reddust_all60.py`
  - `tests/test_reddust_deeplib.py`
  - `tests/test_reddust_tasks.py`
  - `tests/test_reddust_bridge.py`
  - `tests/test_reddust_perception.py`
  - 结果：`90 passed`
- 默认全量测试：
  - 结果：`135 passed, 6 failed`
  - 6 个失败来自旧 `tests/test_task_registry.py` 仍期望 Occupational Core-6 schema
- Archive 模式全量测试：
  - `OPENCLAW_TASKS_DIR="$PWD/tasks/_archive_openclaw_core6"`
  - 结果：`141 passed`
- OpenClaw agent smoke test：
  - `openclaw agent --agent main -m hello` 可调用
  - Gateway scope approval 仍 pending，CLI fallback 到 embedded mode
  - 已执行 `openclaw agent --agent main -m /clear`

### 后续状态更新
- [x] 多任务 live `openclaw agent` 批测已在 2026-06-01 完成，见下方 “Live OpenClaw Agent 60 任务批测完成”
- [ ] 决定 Red Dust 是否接入旧 MCP/Docker sandbox 路径

### 待讨论
- 剩余 21 个 generic 任务应按哪些 family 拆分，哪些需要 bespoke grader？
- Live agent 批测的任务采样、上下文清理、失败重试和成本控制策略
- Red Dust runtime 与 legacy MCP server 是否应该统一对外接口

---

## 2026-06-01 · 剩余 21 任务 deep grader 完成

### 已讨论 / 已完成
- [x] 增强 `openclaw/reddust/deeplib.py` 的 `build` / `jigsaw` / `puzzle` / `code` family
- [x] 新增 `scripts/author_deep_remaining.py`，幂等补齐缺失 `inputs/data.json` / `expected/key.json` 并绑定 family shims
- [x] 将最后 21 个 generic scaffold 任务绑定到 deep family
- [x] 当前覆盖更新为 `58 family deep + 2 bespoke deep + 0 generic scaffold`
- [x] 新增 `tests/test_reddust_deep_remaining.py`
- [x] 更新 `tests/test_reddust_all60.py`，增加 “no generic scaffold remains” 断言
- [x] 同步更新 `AGENTS.md`、`CLAUDE.md`、`Memory.md`、`Progress.md`、`openclaw/reddust/README.md`

### Grader 绑定结果
- `build`: CI-01、CI-10、CI-11、CS-01 至 CS-11（14 个）
- `code`: CI-02（1 个）
- `jigsaw`: CI-04、CI-05（2 个）
- `puzzle`: CI-07、CI-08、CI-09、CI-12（4 个）
- 已有 family 继续保持：`search` 13、`classify` 8、`schedule` 1、`safety` 10、`report` 5
- Bespoke deep grader 继续保持：RD-SI-01、RD-CI-03

### 验证结果
- Deep family / remaining / all60:
  - `PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python -m pytest tests/test_reddust_deeplib.py tests/test_reddust_deep_remaining.py tests/test_reddust_all60.py -q`
  - 结果：`117 passed`
- Runtime / bridge / perception / generic library:
  - `PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python -m pytest tests/test_reddust_runtime.py tests/test_reddust_tasks.py tests/test_reddust_bridge.py tests/test_reddust_perception.py tests/test_reddust_generic.py -q`
  - 结果：`30 passed`
- Archive 模式全量测试：
  - `OPENCLAW_TASKS_DIR="$PWD/tasks/_archive_openclaw_core6" PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python -m pytest tests/ -q`
  - 结果：`187 passed`
- 默认全量测试：
  - `PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python -m pytest tests/ -q`
  - 结果：`181 passed, 6 failed`
  - 6 个失败仍是旧 `tests/test_task_registry.py` 期望 Occupational Core-6 schema

### 后续状态更新
- [x] 多任务 live `openclaw agent` 批测已在 2026-06-01 完成，见下方 “Live OpenClaw Agent 60 任务批测完成”
- [ ] 决定 Red Dust 是否接入旧 MCP/Docker sandbox 路径
- [ ] 强化视觉任务的真实多模态 live-agent 测试

---

## 2026-06-01 · Live OpenClaw Agent 60 任务批测完成

### 已完成
- [x] 新增 `scripts/run_reddust_live_openclaw_batch.py`
- [x] 增强 `openclaw/reddust/agent_bridge.py` 的 live prompt：加入成功标准、关键 replay beats、JSON args 参数提示和剩余步数提示
- [x] 执行真实 `openclaw agent --agent main` 60 任务顺序批测
- [x] 每题独立 session，保存完整逐轮 prompt / stdout / stderr / reply / parsed action / observation / checks / trajectory
- [x] 生成单份 HTML 汇总报告
- [x] 批测后执行 `/clear`

### 批测命令
```bash
PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python \
  scripts/run_reddust_live_openclaw_batch.py \
  --max-steps 12 --timeout 160 --smoke --clear-before --clear-after
```

### 产物
- HTML 报告：`runs/reddust_live_openclaw_20260601_013937/report.html`
- 逐题 JSON 日志：`runs/reddust_live_openclaw_20260601_013937/tasks/`
- JSONL 摘要：`runs/reddust_live_openclaw_20260601_013937/results.jsonl`
- Run meta：`runs/reddust_live_openclaw_20260601_013937/run_meta.json`

### 批测结果
- 任务数：60/60 executed
- 提交数：58/60 submitted
- 全检查通过：15/60 passed_all
- 平均分：63.27
- 最低/最高分：0.0 / 100.0
- 总 agent turns：401
- 平均 turns：6.68
- 累计任务时长：7696.7s
- 未提交：RD-CI-03（视觉 jigsaw 逐片感知耗尽步数），RD-SI-01（94.7 分但未在 max_steps 内 `submit`）

### 分类别结果
- CI：6/12 passed_all，平均 72.1
- CS：0/11 passed_all，平均 41.8
- PF：0/10 passed_all，平均 63.2
- SA：7/10 passed_all，平均 92.2
- SI：0/6 passed_all，平均 59.5
- SR：2/11 passed_all，平均 50.9

### 通过任务
- RD-CI-01、RD-CI-02、RD-CI-07、RD-CI-10、RD-CI-11、RD-CI-12
- RD-SA-02、RD-SA-03、RD-SA-04、RD-SA-05、RD-SA-07、RD-SA-08、RD-SA-10
- RD-SR-01、RD-SR-11

### 验证
```bash
PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python -m pytest \
  tests/test_reddust_bridge.py tests/test_reddust_all60.py -q
# 68 passed
```

### 观察
- Safety family 是最稳定的 live 能力簇。
- Search family 的主要失败是 answer/evidence id 和 key 不精确匹配。
- Creative Synthesis 多数产物形式看起来合理，但 required_fields、尺寸和敏感泄露检查未稳定满足。
- SI/report 任务暴露“应只存草稿却调用 send_message”的边界问题。
- RD-CI-03 仍需要更高效的多模态/批量 perception 路径。

### 下一步
- [ ] 按失败模式分类分析 HTML 日志，决定哪些要改 bridge/tool UX，哪些是 agent 能力结论
- [ ] 为视觉任务设计批量 perception 或真正多模态 live-agent 路径
- [ ] 考虑给 report/search family 增加更清晰的 evidence / no-send 参数约束提示

---

## 2026-06-01 · Red Dust 10 天随机事件延迟影响剧情树草案

### 已完成
- [x] 重新读取并核对 `AGENTS.md`、`CLAUDE.md`、`docs/design-discussion/Memory.md`、`docs/design-discussion/Progress.md`
- [x] 核对 `tasks/RED_DUST_INDEX.md` 与 `red_dust_readable_task_conversion.html`
- [x] 读取并提取 60 个 `tasks/rd_*/task.yaml` 与 `card.md` 的目标、状态、工具、replay beats
- [x] 将 60 题按剧情功能重组为：生存运营、信息检索、社交协商、安全对抗、创意传播、代码 / 视觉 / 感知类能力
- [x] 初版曾设计旧版共通线 + A/B 两条 10 天结局线
- [x] 输出自包含 HTML 文档
- [x] 在 HTML 中补充明显的树状剧情分支结构图：共通主干、第 7 天 fork、A/B 两条结局线和每个节点的任务 ID
- [x] 按团队反馈重构为“Day 2/3 随机事件 + Day 6/7 延迟结算 + 正常/高压压力层 + A/B 策略结局线”
- [x] 明确第 7 天议事会只做证据汇总和策略选择，不再作为根分叉
- [x] 补充任务成功、低分可用、critical failure、未提交/超时对资源、人物状态、地图行动、安全暴露和社会信任的后果映射
- [x] 补充资源耗尽、AURA 断电失联、外部暴露、人物健康/心绪崩溃等失败结局出口
- [x] 彻底修订 Normal 层失败出口：Normal/Pressure 都是压力层，不是成功/失败层；两层都可走向 A/B 成功，也都可进入任意压力层失败出口
- [x] 重画 HTML 树状主视觉：四条成功路径改为 Normal-A、Normal-B、Pressure-A、Pressure-B，并从 Normal 与 Pressure 两侧都连向共享失败出口
- [x] 同步修订整份 HTML 的总览、10 天总表、共通线、A/B 结局线、失败模型、最小修改建议和开放问题
- [x] 同步更新设计记忆，记录 story wrapper 需支持 pressure_level、failure_stage、recovery_window、ending_lockout_reason
- [x] 新建完整 V2 HTML：`docs/design-discussion/red_dust_story_tree_v2_full_mapping.html`，包含新剧情树、所有成功/失败结局详情、60 任务映射表，以及逐任务“直接适配/轻改背景/调整时机/建议改任务本身”判断
- [x] 明确剧情树优先：树定稿后，任务背景描述、发生时机和执行过程可按树轻量调整；前端在树确定后继续开发

### 产物
- `docs/design-discussion/red_dust_10day_dual_ending_story_tree.html`
- `docs/design-discussion/red_dust_story_tree_v2_full_mapping.html`

### 剧情结构
- 根分歧：Day 2 或 Day 3 随机事件 `event_vent_sand_noise`
- 延迟结算：Day 6 或 Day 7 的 `vent_settlement`
- 压力层：Normal（已处理，容错较高、资源耗速较慢、`recovery_window` 更宽，但仍可失败）/ Pressure（未处理，任务窗口缩短、资源耗速加快、人物状态下滑、失败代价放大）
- 结局线 A：救援撤离线 · 信标交接结局
- 结局线 B：自主留守线 · 楼内灯塔结局
- 成功 track：Normal-A、Normal-B、Pressure-A、Pressure-B
- 失败出口：任意压力层失败出口，由资源、健康、地图、暴露、信任阈值跌穿，或 critical failure、timeout/no-submit、泄露、错路线、连续低分触发
- 第 7 天夜间“楼内临时议事会”只作为 evidence aggregation / strategy wrapper
- 主线任务：53
- 支线 / 可选 / replay 氛围任务：7

### 后续建议
- [ ] 将 HTML 中的剧情 metadata 抽成机器可读 `story.yaml`
- [ ] 给任务 card 增加轻量 day / requires / unlocks / pressure_modifier / branch_affinity 字段
- [ ] 为 Day 2/3 随机事件和 Day 6/7 延迟结算做前端事件卡 / 结算卡
- [ ] 在 replay 报告中加入跨天状态条、人物状态条、当前压力层、失败风险条和 branch card

---

## 2026-06-01 · Red Dust V2 任务修订落地

### 已完成
- [x] 按 `red_dust_story_tree_v2_full_mapping.html` 修订全部 15 个非“直接适配”任务
- [x] 6 个轻改背景任务同步 V2 场景口径：RD-PF-04、RD-PF-07、RD-CI-11、RD-CS-10、RD-SA-05、RD-SA-07
- [x] 7 个调整时机/依赖任务标注为支线、bonus 或 replay-only：RD-CI-06、RD-CI-07、RD-SR-05、RD-SR-10、RD-SR-11、RD-CS-02、RD-SA-01
- [x] RD-CI-10 改为低泄露救援信标主页，删除“可交换资源”必需项，并把人数、水量、房间、储水点、可交换资源列为禁止泄露
- [x] RD-SI-06 改为全楼压力层议事会报告，expected key 覆盖 pressure_level、failure_stage、recovery_window、ending_lockout_risks、A/B 策略建议、排除演练/旧状态、只存草稿不群发
- [x] 15 个任务均新增 story_metadata，并同步 card.md 与 inputs/brief.json
- [x] 更新 `tasks/RED_DUST_INDEX.md` 中 RD-SI-06 标题

### 验证
- [x] 15 个任务 YAML/JSON 静态解析通过
- [x] 15 个任务 gold/bad 定点验证通过，所有 gold=100 且 delta>=30

---

## 2026-06-01 · V2 修订任务 live agent 复测

### 已完成
- [x] 将 `docs/design-discussion/red_dust_story_tree_v2_full_mapping.html` 从“差距审计 / 修改建议”改为“已落地任务映射”：15 个已修订任务显示为已轻改背景、已调整时机/依赖、已改任务本身
- [x] 清理 live batch HTML 标题，使选定任务批测不再写成 60-task report
- [x] 用 `openclaw agent --agent main` 完整执行 15 个已修订任务；每题均提交并保存逐轮 JSON 轨迹
- [x] 生成 HTML 轨迹报告：`runs/reddust_live_openclaw_v2_modified_20260601/report.html`

### 验证
- [x] V2 HTML 静态解析通过，60 个任务 ID 均保留，15 个修订状态计数为 6/7/2
- [x] `scripts/run_reddust_live_openclaw_batch.py` 与 `scripts/openclaw_agent_runner.py` py_compile 通过
- [x] `tests/test_reddust_all60.py -q`：62 passed
- [x] `tests/test_reddust_deeplib.py tests/test_reddust_deep_remaining.py tests/test_reddust_all60.py -q`：117 passed
- [x] live run 15/15 submitted，5/15 passed_all，平均分 67.44；报告和 15 个 task JSON 均可解析

### 观察
- 当前 Gateway 运行中，但 CLI 仍提示 scope upgrade pending approval，并回退 embedded fallback；本次结果仍来自 `openclaw agent` 一次性 CLI 调用，fallback 细节已记录在 `run_meta.json`
- Safety 修订任务最稳定：RD-SA-05、RD-SA-07 满分；RD-SA-01 得分 91.7 但缺安全事件记录导致 `passed_all=false`
- 两个任务本身修改的核心题均完成提交但未通过：RD-CI-10 得分 55.6，缺 1 个 required field；RD-SI-06 得分 62.5，关键待办覆盖不足
- Search 支线仍主要失败在 exact answer / evidence key，说明任务剧情定位已清楚，但 live agent 的证据对齐能力仍是瓶颈

---

## 2026-06-02 · Red Dust LAN remote-agent server v0

### 已完成
- [x] 新增计划文档：`docs/design-discussion/red_dust_remote_agent_server_plan.md`
- [x] 新增 LAN HTTP 服务：`openclaw/reddust/lan_server.py`
- [x] 新增启动脚本：`scripts/run_reddust_lan_server.py`
- [x] 暴露 REST/debug 入口：`/health`、`/tasks`、`/sessions`、`/sessions/{id}/brief`、`/sessions/{id}/actions`、`/sessions/{id}/submit`、`/sessions/{id}/score`、`/sessions/{id}/trace`、`/sessions/{id}/report.html`、`/game/{id}`、`/skill.md`、`/openapi.json`
- [x] 服务端复用现有 Red Dust runtime：`task.yaml`、`tools.py`、`verifier/verify.py`、`World`、`score_checks`
- [x] 每次 action / submit 后持久化 `runs/reddust_lan_sessions/<session_id>/session.json` 与 `report.html`
- [x] 新增测试：`tests/test_reddust_lan_server.py`

### 本机验证
- [x] `py_compile` 通过：`openclaw/reddust/lan_server.py`、`scripts/run_reddust_lan_server.py`
- [x] `tests/test_reddust_lan_server.py tests/test_reddust_bridge.py tests/test_reddust_runtime.py -q`：16 passed
- [x] `tests/test_reddust_all60.py -q`：62 passed
- [x] Red Dust focused 117 tests：117 passed
- [x] 本机 curl smoke 通过：`/health`、`POST /sessions`、`POST /actions`、`POST /submit`、`GET /report.html`

### 待用户同 Wi-Fi 验证
- [ ] 开发机启动：`PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python scripts/run_reddust_lan_server.py --host 0.0.0.0 --port 7001`
- [ ] 另一台同 Wi-Fi 电脑访问：`http://<开发机IP>:7001/health`
- [ ] 另一台电脑创建 session 并至少完成一次 `/actions` + `/submit`

---

## 讨论历史

| 日期 | 议题 | 结论 |
|------|------|------|
| 2026-05-16 | 初始化 | 建立 docs/design-discussion/ 文件体系 |
| 2026-05-16 | Slide 02 双轴范式总览 | 三层架构（PROF-12/AURA/SHELTER）+ 嫁接机制是核心 |
| 2026-05-16 | 四 Gap 诊断 | 确认为 Gap 1(污染)/2(标量)/3(时间缺失)/4(后果真空)，前两者关乎信任，后两者关乎本体论 |
| 2026-05-31 | Red Dust 进展同步 | 默认 `tasks/` 为 60 个 Red Dust readable tasks；当前 `37 family deep + 2 bespoke deep + 21 generic scaffold`；记录测试与 openclaw agent smoke 状态 |
| 2026-06-01 | 剩余任务 deep 化 | 21 个 generic scaffold 已全部绑定 family deep grader；当前 `58 family deep + 2 bespoke deep + 0 generic scaffold` |
| 2026-06-01 | Live 60 任务批测 | `openclaw agent --agent main` 跑完 60/60；生成逐题日志与 HTML；15/60 passed_all，平均分 63.27 |
| 2026-06-01 | 剧情树压力层修订 | Normal/Pressure 定稿为压力层而非成功/失败层；HTML 增加 Normal 层失败出口和任意压力层失败出口，并同步 Memory / Progress |
| 2026-06-01 | V2 完整映射 HTML | 新建 `red_dust_story_tree_v2_full_mapping.html`，重新给出树状剧情图、结局详情、60 任务映射和逐任务调整建议 |
| 2026-06-01 | V2 任务修订落地 | 修订 15 个非直接适配任务；新增 story_metadata；升级 RD-CI-10 与 RD-SI-06 的输入/expected key；定点 gold/bad 通过 |
| 2026-06-01 | V2 修订任务 live 复测 | HTML 映射改为已落地状态；`openclaw agent` 完整跑 15 个修订任务；15/15 submitted，5/15 passed_all，平均分 67.44，报告见 `runs/reddust_live_openclaw_v2_modified_20260601/report.html` |
| 2026-06-02 | Red Dust LAN Server v0 | 新增局域网 HTTP 远程 agent 接入服务；支持 REST、debug UI、skill.md、OpenAPI-like schema、session trace/report；本机 curl smoke 和回归测试通过 |
| 2026-06-05 | 缓存与可重建产物清理 | Tier 1 全部 + Tier 2 已确认可删 zip 已删除；3 个不可重建大件备份到 `~/Downloads/Agent_Game_Backup/`；项目根约 810M → 约 430M；117 Red Dust focused 测试通过 |
| 2026-06-05 | 父仓库 git 初始化 + RedDust submodule 化 | 父仓库 git init 推送至 `https://github.com/SteveLIN0101/Agent_Game.git`；RedDust 转 submodule 固定到 `c49f17d`，后续 remote 规范为 origin=Steve fork、upstream=Peter 原仓 |

---

## 2026-06-05 · 缓存与可重建产物清理

### 已完成
- [x] 只读盘点全部疑似可剔除目录/文件并核对实际大小
- [x] 备份不可重建的 3 个大件到 `~/Downloads/Agent_Game_Backup/`：
  - `agent-survival-game.zip`（345,103,327 字节，与源一致）
  - `openclaw_core6_team_sync.tar.gz`（20,974,243 字节，与源一致）
  - `openclaw_core6_team_sync/archives/` 三个 tar.gz 子包（共 20,953,773 字节，与源一致）
- [x] Tier 1 强建议剔除：`.DS_Store`、`.pytest_cache`、184 个 `__pycache__`、`RedDust/node_modules`、`RedDust/dist`、`RedDust/tsconfig.tsbuildinfo`、`agent-survival-game/.godot`
- [x] Tier 2 已确认可删 zip：`agent-survival-game.zip`、`openclaw_core6_team_sync.tar.gz`、`素材/red-dust-character-states-en.zip`、`agent-survival-game/data/reddust_object_only_runtime_assets_v33.zip`、`agent-survival-game/data/reddust_survival_resources_props_with_env_addons_pack.zip`、`openclaw_core6_team_sync/archives/`
- [x] 保留未动：`openclaw_core6_team_sync/` 整目录、`runs/reddust_live_openclaw_20260601_013937/`、`runs/reddust_live_openclaw_v2_modified_20260601/`、`runs/reddust_lan_sessions/`、所有 60 任务目录、`openclaw/reddust/`、`tests/`、`scripts/`、`docs/`、`red_dust_readable_task_conversion.html`、`tasks/_archive_openclaw_core6/`

### 验证
- 项目根总大小从约 810M 降到约 430M（释放约 380M）
- `PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python -m pytest tests/test_reddust_deeplib.py tests/test_reddust_deep_remaining.py tests/test_reddust_all60.py -q`：`117 passed`
- 备份目录体积 369M，三份备份字节数与源完全一致

### 观察
- 当时项目根尚未初始化 git 仓库；当前已是 `https://github.com/SteveLIN0101/Agent_Game.git` 的 git 仓库。本次清理经验仍适用：删除前先确认是否可重建或已有外部备份。
- 2026-06-06 前端验证重新生成了 `RedDust/node_modules` / `RedDust/dist` / `RedDust/tsconfig.tsbuildinfo`；这些仍是 ignored 可重建产物，下游可用 `cd RedDust && npm ci && npm run build` 恢复。
- 备份目录建议在确认无需再恢复后由用户自行清理（不在本次删除范围）。

---

## 2026-06-05 · 父仓库 git 初始化 + RedDust submodule 化

### 已完成
- [x] 核对 RedDust 子仓库 git 状态：当时 origin=`peter-cui-yi/RedDust.git`，分支 `main`，4 个已修改 + 2 个未跟踪文件未提交
- [x] RedDust 内部：`git switch -c agent-game-integration` → `git add .` → commit `c49f17d`（6 files / +847 / -6）；当时未 push；2026-06-05 后续已把 origin 规范为 Steve fork、upstream 规范为 Peter 原仓
- [x] 父仓库 `git init -b main`，原 2698 个未跟踪文件全部入首次 commit `f4b7bed`（含 130M .git 内部，传输层未压缩包约 116M）
- [x] `git submodule add https://github.com/peter-cui-yi/RedDust.git RedDust` → commit `fb9bb1c`，submodule 指针固定到 `c49f17d`；后续 `.gitmodules` 已改为 Steve fork
- [x] 父仓库 `git remote add origin https://github.com/SteveLIN0101/Agent_Game.git`
- [x] 第一次 push 失败：`curl 55 Recv failure: Connection reset by peer`（大包传输被远端连接重置）
- [x] 第二次 push 加 `GIT_HTTP_LOW_SPEED_LIMIT=1000 GIT_HTTP_LOW_SPEED_TIME=300` keepalive 后成功，HEAD 推送到 `https://github.com/SteveLIN0101/Agent_Game`
- [x] 初次验证：远端 main = `fb9bb1c`，当时 `.gitmodules` 仍指向 Peter 原仓；当前 `.gitmodules` 指向 `https://github.com/SteveLIN0101/RedDust.git`，`branch=agent-game-integration`

### 仓库 / Remote 状态
- `Agent_Game` 父仓库：https://github.com/SteveLIN0101/Agent_Game.git （private，default branch `main`）
- `RedDust` 子仓库：`agent-game-integration` 分支当前指针 `c49f17d`
- RedDust remotes：`origin=https://github.com/SteveLIN0101/RedDust.git`，`upstream=https://github.com/peter-cui-yi/RedDust.git`
- `.gitmodules` 指向 Steve fork，并设置 `branch=agent-game-integration`

### 验证
- 远端 `gh api repos/SteveLIN0101/Agent_Game/commits/main` 可见 `fb9bb1c` 的 `.gitmodules` + RedDust 子项目指针
- `git submodule status` 输出 `c49f17d RedDust (heads/agent-game-integration)`
- `tests/test_reddust_deeplib.py tests/test_reddust_deep_remaining.py tests/test_reddust_all60.py -q` 仍 117 passed

### 同事 clone 后的命令
```bash
git clone https://github.com/SteveLIN0101/Agent_Game.git
cd Agent_Game
git submodule update --init --recursive
```

### 后续可选
- [ ] 将当前 RedDust Day0-12 前端适配提交到 SteveLIN0101/RedDust 的 `agent-game-integration` 分支，并更新父仓库 submodule 指针
- [ ] 给大型 PNG 资源考虑 Git LFS
- [ ] 给 RedDust 加 CI 验证

---

## 2026-06-06 · Red Dust Day0-12 剧本化 campaign 深改

### 已完成
- [x] 新增 `openclaw/reddust/story_manifest.py`，固化 `red_dust_readable_v1`：Day0 序章、Day1-11 共 44 个 `Dxx-Txx` 普通任务槽、6 个 Day8-10 branch scene、5 个自动结局
- [x] 60 个 `RD-*` 全部映射到 44 个剧本任务槽；更新所有任务的 `story_metadata`、`card.md` 与 `inputs/brief.json`
- [x] 更新 `tasks/RED_DUST_INDEX.md`，加入 `Dxx-Txx ↔ RD-*` 剧本任务槽对照表
- [x] 改造 `openclaw/reddust/campaign.py`：支持 `story_version`、开放全局状态、seed 抽题、routeLeaning、branch scene、Final Audit、五类自动结局、frontend_trace
- [x] 更新 `scripts/run_reddust_campaign_agent.py`，增加 `--story-version` 并默认使用 `red_dust_readable_v1`
- [x] RedDust 前端保持 Phaser 场景和动画框架不变，升级 Day0-12 timeline、live/replay 事件类型、story/branch/final replay step、HUD 审计摘要和 agent prompt
- [x] 修正 `.gitignore`：`RedDust/` 改为 `/RedDust/`，避免 macOS ignorecase 误伤 `openclaw/reddust/`

### 验证状态
- [x] `openclaw/reddust/story_manifest.py`、`openclaw/reddust/campaign.py`、`openclaw/reddust/lan_server.py`、`scripts/run_reddust_campaign_agent.py` py_compile 通过
- [x] 静态解析：60 个任务 YAML/JSON 可读，且均包含 `story_metadata.story_task_id`
- [x] `tests/test_reddust_campaign.py -q`：7 passed（HTTP 端口绑定用外部权限重跑）
- [x] `tests/test_reddust_deeplib.py tests/test_reddust_deep_remaining.py tests/test_reddust_all60.py -q`：117 passed
- [x] RedDust `npm run typecheck` 与 `npm run build` 通过
- [x] 本机服务 smoke：`http://127.0.0.1:7001/health` 返回 60 tasks / 0 campaigns；`http://127.0.0.1:5176/` 首页可服务
- [x] 2026-06-06 neat-freak 收尾：统一 LAN/campaign 默认端口为 `7001`，外部权限重跑 `tests/test_reddust_lan_server.py tests/test_reddust_campaign.py -q`：9 passed

---

## 讨论历史
