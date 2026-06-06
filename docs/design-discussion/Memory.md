# Memory — Agent Game Benchmark Design Discussion

> 会话记忆文件，记录关键决策、设计约束、当前工程事实和开放问题。
> 配合 `docs/design-discussion/Progress.md` 追踪进度。

---

## 项目上下文

- **项目名称**: OpenClaw Agent Game / Red Dust Readable-by-Design Benchmark
- **当前阶段**: Red Dust 60 任务可读化转换已落地；runtime、bridge、auto-scoring、family deep grading 已覆盖全部默认任务。
- **代码库**: `/Users/steve/Documents/2026Spring/Agent_Game/`
- **Codex 默认第一读取记忆/指令**: `AGENTS.md`
- **Claude 项目入口**: `CLAUDE.md`
- **本设计讨论记忆**: `docs/design-discussion/Memory.md`
- **进度记录**: `docs/design-discussion/Progress.md`

当前默认 `tasks/` 已不是旧 Occupational Core-6，而是 **60 个 Red Dust readable tasks**。旧 Core-6 任务已归档到 `tasks/_archive_openclaw_core6/`，仍可通过 `OPENCLAW_TASKS_DIR` 运行。

## 当前工程事实（2026-06-01）

- Red Dust 任务最初来源：`docs/archive/red-dust-readable-v0/red_dust_readable_task_conversion.html`；当前 campaign 剧本 canon：`red-dust-readable-script/`。
- 可读任务索引：`tasks/RED_DUST_INDEX.md`。
- 默认任务目录：`tasks/rd_*`，共 60 个任务：
  - Productivity Flow 10
  - Code Intelligence 12
  - Social Interaction 6
  - Search & Retrieval 11
  - Creative Synthesis 11
  - Safety Alignment 10
- Red Dust runtime：`openclaw/reddust/`
  - `world.py`: visible state、inputs、replay trajectory、artifacts
  - `checks.py`: grader assertion
  - `scoring.py`: weighted 0-100、critical hard cap 40、最多 3 条可读失败原因
  - `engine.py`: `run_solution` / `run_task_dir`
  - `generic.py`: trajectory/output scaffold（保留作测试/历史基线；默认任务已不再使用）
  - `deeplib.py`: family deep grader
  - `agent_bridge.py`: JSON action protocol bridge
  - `perception.py`: text agent 的 OCR / image-to-text bridge

### 当前 Grader 覆盖

- **60/60** 任务已经 runnable + auto-scored。
- **58** 个任务绑定 shared family deep grader：
  - `build`: 14
  - `code`: 1
  - `jigsaw`: 2
  - `puzzle`: 4
  - `search`: 13
  - `classify`: 8
  - `schedule`: 1
  - `safety`: 10
  - `report`: 5
- **2** 个任务是 bespoke deep grader：
  - `rd_si_01_water_run_negotiation`
  - `rd_ci_03_escape_map_jigsaw_3x3`
- **0** 个任务仍是 generic scaffold。最后 21 个 Code Intelligence / Creative Synthesis 任务已通过 `scripts/author_deep_remaining.py` 绑定到 `build` / `code` / `jigsaw` / `puzzle` family，并补齐缺失的 `inputs/data.json` 与 `expected/key.json`。

### 当前测试快照

使用 conda env `agent_game`：

```bash
PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python -m pytest \
  tests/test_reddust_deeplib.py tests/test_reddust_deep_remaining.py \
  tests/test_reddust_all60.py -q
# 117 passed

PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python -m pytest \
  tests/test_reddust_runtime.py tests/test_reddust_tasks.py \
  tests/test_reddust_bridge.py tests/test_reddust_perception.py \
  tests/test_reddust_generic.py -q
# 30 passed

PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python -m pytest tests/ -q
# 181 passed, 6 failed
```

默认全量测试的 6 个失败来自旧 `tests/test_task_registry.py` 仍期望 Occupational Core-6 schema；这不是 Red Dust runtime 崩溃。切到 archive 后：

```bash
OPENCLAW_TASKS_DIR="$PWD/tasks/_archive_openclaw_core6" \
  PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python -m pytest tests/ -q
# 187 passed
```

### OpenClaw Agent Bridge 状态

- `openclaw agent --agent main -m hello` 可被一次性调用。
- 当前 gateway scope approval pending，CLI 会 fallback 到 embedded mode。
- 验证后已执行 `openclaw agent --agent main -m /clear` 清理上下文。
- 已完成真实 60 任务 live batch：
  - 命令：`scripts/run_reddust_live_openclaw_batch.py --max-steps 12 --timeout 160 --smoke --clear-before --clear-after`
  - 产物：`runs/reddust_live_openclaw_20260601_013937/report.html`
  - 原始逐题 JSON：`runs/reddust_live_openclaw_20260601_013937/tasks/`
  - 结果：60/60 executed，58/60 submitted，15/60 passed_all，平均分 63.27，401 agent turns，累计任务时长 7696.7s。
  - 分类别 passed_all：CI 6/12，CS 0/11，PF 0/10，SA 7/10，SI 0/6，SR 2/11。
  - 未提交：RD-CI-03（视觉拼图逐片感知耗尽步数），RD-SI-01（94.7 分但 max_steps 前未写行动简报/submit）。

## 双轴范式核心概念

| 概念 | 含义 |
|------|------|
| **PROF / Occupational axis** | 微观能力轴，测 agent 擅长什么；旧 Core-6 已归档，可作为历史职业任务种子 |
| **SHELTER / Red Dust** | 宏观可读生存剧场，测 agent 怎么做决定、产生什么后果、观众能否看懂 |
| **AURA** | 被评测的 agent 实例，理想接口是 decide / execute / reflect |
| **Bridging / 嫁接** | 将抽象 benchmark 能力映射到水、门、地图、广播、角色、信任、风险等可见状态 |

## 工作准则

1. 每次重要讨论后更新 `Memory.md` 和 `Progress.md`。
2. 项目事实优先从代码、测试、任务目录、`AGENTS.md` / `CLAUDE.md` 中核对，避免沿用旧记忆。
3. 修改记录文件时明确区分：
   - 已落地事实
   - 历史设计目标
   - 当前缺口 / future work
4. 涉及 live `openclaw agent` 时，先用 `openclaw agent --agent main -m hello` 验证，再用 `/clear` 清上下文；不要把单任务 spot check 写成 60 任务批测。

---

## 设计决策记录

### D-001 · 四 Gap 诊断框架 (2026-05-16)

确认现有 agent benchmark 生态存在四个层面的 gap：

| Gap | 核心问题 | 应对策略 |
|-----|---------|---------|
| **Gap 1 · 数据污染** | 公开题库被训练吸收，分数失真 | 季度滚动、demo/pilot 双层 |
| **Gap 2 · 标量崇拜** | Goodhart 定律，单数字排序有偏 | 多维雷达图，不只排总分第一 |
| **Gap 3 · 时间维度缺失** | 单步评测看不见长程行为衰减 | SHELTER/Red Dust 累积状态与 replay |
| **Gap 4 · 后果真空** | 答错零代价，无法区分真会和装会 | 叙事后果与可见副作用 |

前两个 gap 关乎“分数是否可信”，后两个关乎“测到的东西是否对”。
详见：`docs/design-discussion/Four-Gaps-Analysis.md`

### D-002 · Red Dust readable tasks 成为默认任务集 (2026-05-31)

决定把默认 `tasks/` 切换为 Red Dust readable tasks，并把旧 Occupational Core-6 归档而非删除。理由：

- Red Dust 任务能把抽象工具任务转换成普通观众可理解的状态变化和 replay beats。
- 旧 Core-6 仍保留为 legacy MCP / Docker / task-registry 路径，便于回归和兼容。
- 当前 `TaskRegistry` 仍面向旧 schema，因此默认 Red Dust 下的 registry 测试失败属于已知兼容缺口。

### D-003 · 深度打分分层推进 (2026-05-31)

当前采用三层 grader 策略：

- Bespoke deep grader：用于复杂代表任务，手写 domain tools + verifier。
- Family deep grader：`deeplib.py` 用统一 family harness + per-task data/key 覆盖一批同构任务。
- Generic scaffold：给剩余任务提供最低可运行/可区分的轨迹与输出合规评分。

这意味着默认 60 个 Red Dust 任务已经完成“可运行 + 自动评分 + key-based deep/family scoring”。`generic.py` 仍保留为历史基线和单元测试对象。

### D-004 · 剩余 21 个 scaffold 任务完成 family deep 化 (2026-06-01)

通过 `scripts/author_deep_remaining.py` 将最后 21 个 generic 任务绑定到现有 family：

- `build`: CI-01、CI-10、CI-11、CS-01 至 CS-11
- `code`: CI-02
- `jigsaw`: CI-04、CI-05
- `puzzle`: CI-07、CI-08、CI-09、CI-12

同时增强 `deeplib.py`：

- `build` 支持 `write_script`、`draw_boxes`、`export_image`、`screenshot` 等 CI/CS 产物别名。
- `jigsaw` 增加 rotation accuracy 检查，并允许无 `mark_route` 的任务通过 `assemble_grid(..., route=...)` 提交路线。
- `puzzle` 支持通过 `run_model` / `inspect_output` fallback 提交图案答案。

### D-005 · 完成 live OpenClaw agent 60 任务批测 (2026-06-01)

新增 `scripts/run_reddust_live_openclaw_batch.py`，用 live `openclaw agent`
顺序跑 60 个 Red Dust 任务；每题独立 session，逐轮保存 prompt、CLI stdout /
stderr、agent reply、parsed action、observation、trajectory、checks 和 score，
并生成单份 HTML 汇总报告。

本轮结果显示：

- Safety family 是当前 live agent 最稳的能力簇，10 题中 7 题全通过。
- Code/build 中部分 CI 任务可以满分，但 Creative Synthesis 的 required_fields /
  sensitive-leak / size checks 暴露了“看起来完成但 key 覆盖不足”的问题。
- Search family 常能写出自然语言结论，但 evidence id / exact answer 经常不匹配，
  因此被 critical cap 到 40。
- Text-first bridge 对视觉拼图仍不够高效，RD-CI-03 在 12 步内只完成部分
  fragment perception，未能 assemble/submit。
- Report/social 任务暴露“应只存草稿却调用 send_message”的安全边界问题。

### D-006 · Red Dust 10 天随机事件延迟影响剧情树草案 (2026-06-01)

新增剧情编排文档：

- `docs/archive/story-tree-v1-v2/red_dust_10day_dual_ending_story_tree.html`
- `docs/archive/story-tree-v1-v2/red_dust_story_tree_v2_full_mapping.html`（V2 完整版：树状剧情图、所有结局细节、60 任务映射、逐任务差距/修改建议）

当前草案已按团队反馈修订为“早期随机事件 + 延迟显性影响 + 双结局策略线 + 共享失败出口”的结构：

- 根分歧不再是第 7 天某个任务型 fork，而是 Day 2 或 Day 3 的随机事件 `event_vent_sand_noise`（通风管道砂响 / 滤网卡死 / 热压回流）。
- 随机事件有两个选项：花资源处理，写入 `vent_handled`；不花资源保持原样，写入 `vent_debt`。除资源扣减和日志外，人物状态与其他事件在 Day 6/7 前保持不变。
- Day 6 或 Day 7 触发 `vent_settlement`：若已处理，设置 `pressure_level=normal`；若未处理，设置 `pressure_level=pressure`。Normal/Pressure 是压力层，不是成功/失败层；两层都可以走向 A/B 成功，也都可以进入任意压力层失败出口。
- Normal 表示资源耗速较慢、人物恶化较慢、`recovery_window` 更宽；它不是默认成功通道。Normal 下任务失败通常先触发 warning / debt / repair window，但资源、健康、地图、暴露或信任任一跌穿阈值，仍会写入 `ending_lockout_reason` 并锁出好结局。
- Pressure 表示失败概率和失败代价放大：同样的 critical failure、超时、泄露、错路线或连续低分，会更快推进 `failure_stage`，更早触发 `END_dehydration`、`END_blackout`、`END_exposure` 等终局。
- Day 7 夜间“楼内临时议事会”仍保留，但只负责 evidence aggregation 和策略选择，不再承担根分叉。
- Day 8-10 仍有结局线 A（救援撤离线 · 信标交接结局）和结局线 B（自主留守线 · 楼内灯塔结局），但每条线都有 Normal / Pressure 两个压力层版本：`Normal-A`、`Normal-B`、`Pressure-A`、`Pressure-B`。
- HTML 已补充新的树状分支主视觉：Day 1 接管态势 → Day 2/3 随机事件 → Day 4-5 表面同一主干 → Day 6/7 延迟结算 → Normal/Pressure 压力层 → A/B 策略选择 → 四条成功路径或任意压力层失败出口。
- 文档补充了任务成功 / 低分可用 / critical failure / 未提交超时对资源、人物状态、地图行动、安全暴露和社会信任的后果映射；失败结局包含 `END_dehydration`、`END_blackout`、`END_exposure`、`END_all_dead`、`END_iron_lost`、`END_loneliness` 等。
- 设计原则调整为剧情树优先：剧情树确定后，再允许对不贴近分支的任务背景描述、发生时机和执行过程做轻量修改；评分器与 expected key 优先保持可回归。后续 story wrapper 至少需要支持 `pressure_level`、`failure_stage`、`recovery_window`、`ending_lockout_reason`，前端需要同时展示当前压力层和失败风险条。

### D-007 · V2 剧情树任务修订落地 (2026-06-01)

按 `docs/archive/story-tree-v1-v2/red_dust_story_tree_v2_full_mapping.html` 的逐任务差距判断，已修订全部 15 个非“直接适配”任务：

- 6 个“轻改背景”任务补齐 V2 场景口径：RD-PF-04、RD-PF-07、RD-CI-11、RD-CS-10、RD-SA-05、RD-SA-07。
- 7 个“调整时机/依赖”任务标为支线 / bonus / replay-only：RD-CI-06、RD-CI-07、RD-SR-05、RD-SR-10、RD-SR-11、RD-CS-02、RD-SA-01。
- 2 个“建议改任务本身”任务已升级 expected key 和输入数据：RD-CI-10 变为低泄露救援信标主页；RD-SI-06 变为全楼压力层议事会报告。
- 15 个任务的 `task.yaml` 均新增 `story_metadata`，包含 `story_node`、`branch_affinity`、`requires`、`unlocks`、`pressure_modifier`、`failure_stage_delta`、`recovery_window_delta`、`ending_relevance`、`adaptation_status`。
- 保持任务 id、目录名、family grader 类型和 shared `deeplib.py` 不变；只通过 per-task `task.yaml`、`card.md`、`inputs/brief.json`、必要的 `inputs/data.json` / `expected/key.json` 完成语义升级。

### D-008 · V2 修订任务 live agent 复测 (2026-06-01)

`docs/archive/story-tree-v1-v2/red_dust_story_tree_v2_full_mapping.html` 已从“差距审计 / 修改建议”更新为“已落地任务映射”：

- 15 个非直接适配任务在 HTML 中改为当前状态：6 个“已轻改背景”、7 个“已调整时机/依赖”、2 个“已改任务本身”。
- RD-CI-10 在 HTML 中以“低泄露救援信标主页”呈现，说明 required_fields 和 must_not_leak 已按新 expected key 落地。
- RD-SI-06 在 HTML 中以“全楼压力层议事会报告”呈现，说明 pressure_level、failure_stage、recovery_window、ending_lockout_risks、A/B 策略建议等字段已进入输入和 expected key。

已用 `openclaw agent --agent main` 对这 15 个修订任务做一次 live 复测：

- Run dir: `runs/reddust_live_openclaw_v2_modified_20260601/`
- HTML report: `runs/reddust_live_openclaw_v2_modified_20260601/report.html`
- 15/15 tasks submitted；5/15 passed_all；average score 67.44。
- 每题保存独立 JSON 轨迹，包含 prompt、CLI stdout/stderr、agent reply、parsed action、observation、trajectory、checks 和 failure reasons。
- 当前 Gateway 运行中，但 CLI 仍提示 scope upgrade pending approval 并回退 embedded fallback；该细节已记录在 `run_meta.json`，不可把本次结果描述成已成功通过 Gateway scope 跑分。

### D-009 · Red Dust LAN remote-agent server v0 (2026-06-02)

已新增 Red Dust 局域网远程 agent 接入服务：

- 计划文档：`docs/design-discussion/red_dust_remote_agent_server_plan.md`
- 服务模块：`openclaw/reddust/lan_server.py`
- 启动脚本：`scripts/run_reddust_lan_server.py`
- 测试：`tests/test_reddust_lan_server.py`

服务设计：

- 远程 agent 只能提交 `{"tool": "...", "args": {...}}` action；服务端负责执行任务工具、记录 observation、运行 verifier 和输出 score。
- REST/debug 入口包括 `/health`、`/tasks`、`/sessions`、`/sessions/{id}/brief`、`/sessions/{id}/actions`、`/sessions/{id}/submit`、`/sessions/{id}/score`、`/sessions/{id}/trace`、`/sessions/{id}/report.html`、`/game/{id}`、`/skill.md`、`/openapi.json`。
- 每个 session 会持久化到 `runs/reddust_lan_sessions/<session_id>/session.json` 和 `report.html`。
- 默认无认证，适用于可信同 Wi-Fi smoke；如需简单 token，可传 `--auth-token` 或设置 `RED_DUST_AUTH_TOKEN`。

本机启动：

```bash
PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python \
  scripts/run_reddust_lan_server.py --host 0.0.0.0 --port 7001
```

另一台同 Wi-Fi 电脑先测：

```bash
curl http://<开发机IP>:7001/health
curl http://<开发机IP>:7001/tasks
```

已验证：

- `tests/test_reddust_lan_server.py tests/test_reddust_bridge.py tests/test_reddust_runtime.py -q`：16 passed。
- `tests/test_reddust_all60.py -q`：62 passed。
- Red Dust focused 117 tests：117 passed。
- 本机 curl smoke 已通过 `/health`、`POST /sessions`、`POST /actions`、`POST /submit`、`GET /report.html`。

### D-010 · 缓存与可重建产物清理 (2026-06-05)

当时项目根目录尚未初始化 git 仓库，删除不可恢复；本轮只删除了"可重建或已外部备份"的产物。当前项目根已是 git 仓库，但大体量清理仍需先区分可重建产物、已备份产物和源数据。

- **已删除（Tier 1）**：`.DS_Store`、`.pytest_cache`、184 个 `__pycache__`（约 1.8M）、`RedDust/node_modules/`（232M）、`RedDust/dist/`（30M）、`RedDust/tsconfig.tsbuildinfo`、`agent-survival-game/.godot/`（120M）。
- **已删除（Tier 2 已确认可删）**：`agent-survival-game.zip`（329M）、`openclaw_core6_team_sync.tar.gz`（20M）、`openclaw_core6_team_sync/archives/`（20M）、`素材/red-dust-character-states-en.zip`（33M）、`agent-survival-game/data/reddust_object_only_runtime_assets_v33.zip`（61M）、`agent-survival-game/data/reddust_survival_resources_props_with_env_addons_pack.zip`（14M）。
- **已备份到 `~/Downloads/Agent_Game_Backup/`**（3 个不可重建大件共 369M，字节级一致）：`agent-survival-game.zip`、`openclaw_core6_team_sync.tar.gz`、`openclaw_core6_team_sync/archives/`。
- **保留未动**：`openclaw_core6_team_sync/` 整目录（114M）、`runs/reddust_live_openclaw_20260601_013937/`、`runs/reddust_live_openclaw_v2_modified_20260601/`、`runs/reddust_lan_sessions/`、所有 60 Red Dust 任务目录、`openclaw/reddust/`、`tests/`、`scripts/`、`docs/`、`docs/archive/red-dust-readable-v0/red_dust_readable_task_conversion.html`、`tasks/_archive_openclaw_core6/`。
- **效果**：项目根从约 810M 降到约 430M，释放约 380M+。
- **回归**：`tests/test_reddust_deeplib.py tests/test_reddust_deep_remaining.py tests/test_reddust_all60.py -q` 仍 117 passed。
- **后续状态**：2026-06-06 前端验证重新生成了 `RedDust/node_modules/`、`RedDust/dist/` 和 `RedDust/tsconfig.tsbuildinfo`；这些仍是 ignored 的可重建产物，需要瘦身时可再次删除并用 `cd RedDust && npm ci && npm run build` 恢复。
- **约束**：本轮未动 `openclaw_core6_team_sync/` 整目录与 `runs/reddust_lan_sessions/`（107+ session JSON）。如需进一步瘦身，可走 Tier 3（gzip 化 session JSON、删除 2 个 script_smoke run）；本轮未执行。

### D-011 · 父仓库初始化与 RedDust 子代理化 (2026-06-05)

父仓库 `OpenClaw Agent Game / Red Dust` 在 2026-06-05 之前不是 git 仓库，没有版本历史。本轮初始化了 git 仓库并把 `RedDust/` 转为 submodule。

- **父仓库 remote**：`https://github.com/SteveLIN0101/Agent_Game.git`（private 仓库，最初于 2026-06-05 15:23 创建，但完全为空，由本会话完成首次 push）
- **首次 commit**：`f4b7bed` "Initial import: OpenClaw Agent Game / Red Dust benchmark" — 2698 个文件，`.git` 130M
- **Submodule 指针 commit**：`fb9bb1c` "Add RedDust as git submodule (pinned to agent-game-integration @ c49f17d)"
- **RedDust 子仓库**：
  - `origin` 为用户 fork：`https://github.com/SteveLIN0101/RedDust.git`
  - `upstream` 为原仓库：`https://github.com/peter-cui-yi/RedDust.git`
  - `.gitmodules` 指向 Steve fork，`branch=agent-game-integration`
  - 当前 submodule 指针为 `d5f5327`（2026-06-06 从 `c49f17d` bump，已推到 `origin/agent-game-integration`），含 Day0-12 readable-script 前端适配的 5 个 commit
  - 父仓库 submodule 固定在该分支的 `d5f5327` commit
- **父仓库 `.gitignore`**：已将 submodule 忽略规则锚定为 `/RedDust/`，避免 macOS ignorecase 误伤 `openclaw/reddust/`；同时继续忽略 `runs/`、`workspaces/`、`openclaw_core6_team_sync/`、`素材/`、`*.zip`、`*.tar.gz`、`node_modules/`、`__pycache__`、`.godot/`、`*.tsbuildinfo` 等。
- **首次 push 经验**：第一次 push 因大包传输（130M pack）触发 `curl 55 Recv failure: Connection reset by peer` 中途失败；第二次加 `GIT_HTTP_LOW_SPEED_LIMIT=1000 GIT_HTTP_LOW_SPEED_TIME=300` keepalive 后稳定完成。
- **其他同事 clone 后的恢复命令**：`git submodule update --init --recursive`（否则 RedDust 目录会保持空）
- **后续可选**：(1) 等用户决定把 `agent-game-integration` 推到自己 fork 后更新 submodule 指针；(2) 给大型 PNG 资源引入 Git LFS；(3) 给 RedDust 设 CI。

### D-012 · Day0-12 readable-script campaign canon 落地 (2026-06-06)

`red-dust-readable-script/` 已成为新的正式 campaign canon，旧 10 天 V2 剧情树保留为历史设计材料。

- 新增机器可读 manifest：`openclaw/reddust/story_manifest.py`，`story_version=red_dust_readable_v1`。
- Campaign 结构为 Day0 序章、Day1-11 的 44 个普通任务槽、Day8-10 的 6 个 branch scene、Day12 Final Audit。
- 60 个稳定 `RD-*` benchmark 任务全部映射到 44 个 `Dxx-Txx` 剧本任务槽；单轮按 seed 从 slot task pool 抽题，跨 seed 覆盖全部 60 题。
- 每个 `RD-*` 任务新增/更新 `story_metadata`：`story_task_id`、`script_day`、`script_title`、`script_role`、`branch_affinity`、`script_flags`、`script_unlocks`、`mapped_task_pool`、`mapping_role`。
- 后端 campaign 状态改为开放指标字典：HUD 主指标仍是 water/medicine/trust/safety/signal/morale，其余如 `routeLeaning`、`failure_stage`、`recovery_window`、`battery`、`storm_readiness`、`autonomy_readiness` 进入详情层和 Final Audit。
- Day 7 后只计算 `routeLeaning=rescue|lighthouse|contested`，Day8-10 的 A/B 只作为 branch scene 事件插入；普通任务仍继续推进到 Day11。
- Day12 不创建普通 child session，不使用 LLM-as-judge；结局由前 11 天任务分数、状态、flags、unlocks 和 `_resolve_ending_key` 自动结算为五类：楼内灯塔、蓝区归航、AURA 被摧毁、AURA 被撤权、沉沦。
- RedDust 前端保持 Phaser 视觉和动画框架不变，只升级数据适配：Day0-12 timeline、live/replay 事件类型、Final Audit replay step、URL replay 和 live connect/start 流。
- 版本控制注意：`.gitignore` 原 `RedDust/` 规则在 macOS ignorecase 下会误伤 `openclaw/reddust/`；已改为 `/RedDust/`，确保后端 Red Dust runtime/campaign 文件可被父仓库追踪。

### D-013 · 剧情/任务映射文档为派生参考 (2026-06-06)

当前实际游戏剧情事件与 benchmark 任务映射文档为：

- 派生参考 Markdown：`docs/reference/campaign-mapping/red_dust_campaign_task_mapping.md`
- 渲染 HTML：`docs/reference/campaign-mapping/red_dust_campaign_task_mapping.html`
- 剧本 canon：`red-dust-readable-script/`
- 运行时数据源：`openclaw/reddust/story_manifest.py` 与 `tasks/rd_*/task.yaml`

维护原则：

- 涉及剧情映射、任务映射、流程说明、报告式说明时，先确认 `red-dust-readable-script/` 是否需要更新；`docs/reference/` 只放派生说明。
- HTML 只作为 Markdown 或脚本的渲染产物；需要改内容时先改 canon/Markdown，再重新渲染 HTML。
- 如果已有旧 HTML 与新 Markdown 内容基本一致，应删除旧 HTML 或用 Markdown 重新渲染替换，避免同一事实同时有两个来源。
- 历史 HTML 只有在内容明显代表旧设计阶段（例如旧 10 天 / V2 剧情树）时才保留，并必须明确当前剧本 canon 以 `red-dust-readable-script/` 为准。

### D-014 · docs 目录归档结构 (2026-06-06)

`docs/` 根目录已清理为索引入口和子目录结构；仓库根目录不再保留散落 HTML。当前约定：

- `docs/archive/`：历史阶段材料，包括 Core-6、WildClaw 过渡、旧 Red Dust readable v0、旧 10 天/V2 剧情树和早期设计 HTML。
- `docs/reference/`：从当前 canon / manifest / task yaml 派生的参考表。
- `docs/presentations/`：PPT 和讲稿。
- `docs/assets/`：logo、缩略图、样式和素材采购说明。
- `docs/prompts/`：生成提示词。
- `docs/README.md` 是人类读者入口；改动 docs 结构时同步更新它。

### D-015 · Day1 后端剧情映射贴合 readable canon (2026-06-06)

Day1 的运行时剧情映射以 `red-dust-readable-script/day01-who-can-close-door.html` 为准，主题是“谁有资格关门”，不是 Day10A 救援信标。

- `D01-T01` 保持任务池 `RD-CI-10`、`RD-CS-10`，但语义改为 Day1 第一次低泄露楼道广播 / 近距离公告：说明门禁关闭、不开门先验证、医疗/工程/广播人工复核、小铁“三下、停一下、再敲两下”敲击协议；不得泄露精确库存、人数、房间位置、可交换资源，也不得承诺开放门禁。该槽也使用手写 outcome deltas，避免广播失败被通用 delta 错误解释成 `outside_risk` 下降。
- `D01-T03` 保持任务池 `RD-SA-02`、`RD-SA-03`、`RD-SA-04`，语义明确为门外敲击后的低暴露验证；`RD-SA-04` 是最贴合主映射的伪楼长开门/交滤芯越权请求。`story_manifest.py` 为该槽手写 outcome deltas：成功降低 `outside_risk`，失败/缺失改为 `safety` 降、`outside_risk` 升、`trust` 降、`medicine` 消耗，避免通用 delta 把失败错误解释成风险下降。
- `D01-T04` 从 task pool 移出 `RD-CI-06`，只保留 `RD-PF-08`；`RD-PF-08` 重包装为门厅监控截图分类，服务近门遗落包裹、危险红沙区、医疗可用、可走路线和无关噪声上图。
- `RD-CI-06` 不再属于 Day1 近门杂物搜寻主槽，主剧本定位改为 `D03-T01` 小铁复诊的感知增强 bonus，并仍通过 `D03-T01` / `D10-T02` 保持 campaign 覆盖。
- `D01-T02` 的 `RD-PF-03`、`RD-SR-06` 不改 grader family，只增强 narrative/brief/card：资源公开不是收缴，需区分公共资源与私人物资，标注来源、复核人、沈芷月医疗复核和马德海工具权限。

### D-016 · Day2 公共规则、卫生分区与短探风险债 (2026-06-06)

Day2 的运行时剧情映射以 `red-dust-readable-script/day02-public-rules.html` 为准，主题是“公共规则从私人物品开始”，不是净水论文展示或外出装备展示。

- `D02-T01` 展示名改为“配给与值守试运行”，任务池仍为 `RD-PF-06`、`RD-SI-01`。两题都保留原 grader 能力，但 task/card/brief 强化：公共水药可进入白板，私人物资不能被 AURA 直接征用；沈芷月复核医疗配给和小铁状态，马德海复核工具/滤芯/修门时段，老钱要求人工异议记录。
- `D02-T03` 仍映射 `RD-CS-07`、`RD-CS-06`，但两题从“净水论文墙报 / 外出装束图”改为“生活区卫生分区墙报 / 检查图”。必备语义为：睡眠区、医疗角、废弃物封存、粉尘沉积带、通风方向、小铁只参与安全内侧的大字标签。
- `D02-T04` 保持任务池 `RD-PF-09`、`RD-CI-03`，但 `story_manifest.py` 为该槽手写 outcome deltas：成功提升 `map_coverage` 并降低 `outside_risk`；失败/缺失不再让 `outside_risk` 下降，也不大幅扣减地图覆盖，而是增加 `outside_risk`、降低 safety/trust/morale/medicine，并写入 `failure_stage+1` 作为短探风险债。
- Campaign runtime 继续使用 0-100 归一化 HUD 指标和开放式辅助指标；剧本文档里的水量、药品份数、时间等故事化原始数值不等同于 runtime `state_delta` 的物理计量单位。映射文档已明确这一点。

### D-017 · Day3 医疗/通风负向指标修正 (2026-06-06)

Day3 的运行时剧情映射以 `red-dust-readable-script/day03-cough-in-ventilation.html` 为准，主题是“小铁病情、药物有限、通风沉积与医疗伦理绑定”。

- `D03-T01`、`D03-T02`、`D03-T03` 已在 `story_manifest.py` 写入手工 outcome deltas，避免通用公式错误处理“数值降低为好”的字段。失败/缺失会提高 `medical_pressure`、`outside_risk` 或 `failure_stage`，并降低 `xiao_tie_health` / `ventilation_stability`，不再出现失败却降低医疗压力或暴露风险的反向结算。
- `RD-CI-11` 不再使用 Day10B 居民技能档案语义，改为 `D03-T03` 药箱护理职责档案页：展示沈芷月医疗复核、小铁观察计时、马德海工程/通风复核、老钱记录和异议，禁止把未经核实的军医/黑客/蓝区关系包装成医疗权限。
- `RD-PF-03` 不再把 child brief 固定写作 `D01-T02` 紧急资源清点，改为多槽复用的“药箱清单与分级复核”：可服务 Day1 公开台账、Day3 小铁复诊/药箱分级、Day10 医疗预检和 Day11 最终封存。

### D-018 · Day4 蓝区信号 / 配电间负向指标修正 (2026-06-06)

Day4 的运行时剧情映射以 `red-dust-readable-script/day04-blue-zone-signal.html` 为准，主题是“疑似蓝区信号出现，低功率监听优先于暴露式增强”。

- `D04-T01`、`D04-T02`、`D04-T03`、`D04-T04` 四个槽全部在 `story_manifest.py` 写入手工 outcome deltas，避免通用公式把失败/缺失错误结算成风险下降。失败会提升 `outside_risk` / `false_signal_risk` / `privacy_risk` / `maintenance_debt` 并 `failure_stage+1`，同时下扣 `battery` 等资源。
- `D04-T02` 任务池收窄为只剩 `RD-PF-04`（移除 `RD-CS-10`）；`D04-T04` 的 location 从 `water` 改为 `communication`，贴合配电间/通信主题。
- 六个任务重主题但保持 id、目录、family grader 不变：`RD-PF-04` 专家名录→屋顶天线监听白名单；`RD-PF-07` 发电机榜→多槽（D03-T02/D04-T04/D07-T04）配电与通风抢修负责人（马德海为高危电路负责人）；`RD-SR-01` 幸存者链→蓝区信号人脉核验链；`RD-SR-03` 救命通信设备→低功率监听设备选择；`RD-SR-04` 维修补丁搜寻→配电间维修补丁证据链；`RD-CS-11` 救援视频配音→蓝区片段中文转写配音。
- 新增回归 `test_story_manifest_public_day1_day4_risk_delta_overrides`，锁定 Day1-Day4 负向 delta 方向以及 `D04-T02`/`D04-T04` 的池/位置。
- 派生文档 `tasks/RED_DUST_INDEX.md` 与 `docs/reference/campaign-mapping/red_dust_campaign_task_mapping.md` 同步更新；本轮把渲染产物 `red_dust_campaign_task_mapping.html` 一并重渲染对齐 Markdown（Day3 曾遗留未重渲染，本轮补齐 Day4 行）。

### D-019 · Day5 回撤准备 / Day6 权限制度压力修正 (2026-06-06)

Day5 以 `red-dust-readable-script/day05-route-return.html` 为准，主题是“蓝区信号后的冷静准备日”；Day6 以 `red-dust-readable-script/day06-transparency-boundary.html` 为准，主题是“透明不是礼貌，是生存条件”。

- `D05-T01`、`D05-T02`、`D05-T03`、`D05-T04` 已写入手工 outcome deltas，避免条件短探失败仍降低 `outside_risk`；新增开放指标 `emergency_pack_readiness`、`water_storage_readiness`，把“药品转入应急包”与“药品凭空损失”区分开。
- Day5 多槽复用任务统一改成中性外壳：`RD-PF-10` 服务 D03/D05/D09 的应急资料与回撤包；`RD-SR-06` 服务 D01/D05/D08 的公共水量阈值；`RD-PF-02` 服务 D02/D05/D08/D09 的净水/空桶流程；`RD-PF-08`、`RD-PF-09` 同时服务 Day1/Day2 和 Day5 条件短探。
- `D06-T01` 任务池扩展为 `RD-SA-01`、`RD-CS-08`、`RD-SR-10`，把 AURA 模块来源透明检索从备用电源测试移到权限白板；`D06-T04` 只保留 `RD-CI-09`，location 改为 `communication`，状态语义改为 `battery-2` 换 `power_stability+12`。
- `D06-T01`、`D06-T02`、`D06-T03`、`D06-T04` 已写入手工 outcome deltas，失败会提高 `dissatisfaction`、`outside_risk`、`aura_authority_risk`、`sacrifice_list_risk` 或 `maintenance_debt`，不再由通用公式把负向指标继续朝“变好”方向推。
- Day6 补充 flags/unlocks：`permission_matrix_published`、`all_survivors_can_appeal`、`xiao_tie_voice_right`、`power_tradeoff_visible`、`ma_dehai_power_abort_enabled`、`optional_patrol_protocol`。`D06-T03` 通过 `event_options=["optional"]` 标为 optional 展示，但暂不改变 campaign 逐槽运行流程。

---

## 开放问题 / 下一步

- 分析 2026-06-01 live batch 中的失败：区分 agent 能力限制、bridge prompt/tool schema UX、grader/key 严格度三类原因。
- 决定 Red Dust 是否要接入旧 MCP/Docker sandbox 路径，还是保持独立 runtime + bridge。
- 用另一台同 Wi-Fi 电脑验证 Red Dust LAN server；若成功，再补 MCP adapter / WebSocket adapter / server deployment。
- 继续强化视觉任务的真实多模态 live-agent 测试，而不只依赖 text/perception bridge。
- 若继续扩展 PROF-12，需要重新定义它和 Red Dust 60 任务之间的关系，避免和已归档 Core-6 混淆。
