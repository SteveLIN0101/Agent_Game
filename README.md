# OpenClaw Agent Game / Red Dust

OpenClaw Agent Game 是一个可游玩的 agent benchmark。当前核心是 **Red Dust
Readable-by-Design**：60 个可自动评分的 `RD-*` 任务被嵌入同一个生存剧情世界中。

当前正式 campaign canon 是 `red_dust_readable_v1`。它把单题任务串成 Day0-12
的一整轮游戏，包含可见状态、回放事件、分支场景和自动结局。

## 目录概览

- `tasks/rd_*`：60 个稳定的 Red Dust benchmark 任务。
- `openclaw/reddust/`：运行时、评分、LAN server、campaign 中间层和剧情 manifest。
- `RedDust/`：React + Phaser 前端 submodule，用于演示、Live Agent Mode 和 Replay Mode。
- `red-dust-readable-script/`：Day0-12 readable-script 剧本 canon，供 campaign manifest 使用。
- `tasks/_archive_openclaw_core6/`：已归档的旧 Occupational Core-6 任务。

## 克隆仓库

```bash
git clone https://github.com/SteveLIN0101/Agent_Game.git
cd Agent_Game
git submodule update --init --recursive
```

`RedDust/` 是 submodule。它的 `origin` 是 SteveLIN0101 fork，`upstream` 是原始
`peter-cui-yi/RedDust` 仓库。

## Python 环境

使用项目 conda 环境：

```bash
PY=/Users/steve/miniconda3/envs/agent_game/bin/python
PYTHONPATH=. $PY -m pytest tests/test_reddust_deeplib.py tests/test_reddust_deep_remaining.py tests/test_reddust_all60.py -q
```

## 运行单个 Red Dust 任务

```bash
PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python \
  scripts/run_reddust_task.py tasks/rd_si_01_water_run_negotiation all
```

## 启动 Campaign 后端

```bash
PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python \
  scripts/run_reddust_lan_server.py --port 7001
```

常用接口：

- `GET http://127.0.0.1:7001/health`
- `POST http://127.0.0.1:7001/campaigns`
- `GET http://127.0.0.1:7001/campaigns/<campaign_id>/trace`
- `GET http://127.0.0.1:7001/campaigns/<campaign_id>/report.html`

Campaign 运行产物会持久化到 `runs/reddust_campaigns/<campaign_id>/`。

## 让 Agent 跑完整 Campaign

```bash
PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python \
  scripts/run_reddust_campaign_agent.py \
  --base-url http://127.0.0.1:7001 \
  --story-version red_dust_readable_v1 \
  --branch-policy auto \
  --connect-agent
```

如果 campaign 是由前端创建的，再加：

```bash
--campaign-id rdcamp-... --wait-for-start
```

## 启动前端

```bash
cd RedDust
npm ci
npm run dev
```

打开：

- Demo：`http://127.0.0.1:5176/`
- Live Agent Mode：`http://127.0.0.1:5176/?mode=live&api=http://127.0.0.1:7001`
- Replay Mode：`http://127.0.0.1:5176/?mode=replay&api=http://127.0.0.1:7001&campaign_id=rdcamp-...`

前端保留现有 Phaser 视觉和动画框架。Live / Replay 只消费后端 campaign 事件：
`story_event`、`task_started`、`action_executed`、`slot_completed`、`branch_scene`、
`final_audit`、`campaign_complete`。

## 验证命令

```bash
PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python -m pytest tests/test_reddust_campaign.py -q
PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python -m pytest tests/test_reddust_deeplib.py tests/test_reddust_deep_remaining.py tests/test_reddust_all60.py -q
cd RedDust && npm run typecheck && npm run build
```

兼容性说明：在默认 `tasks/` 下运行完整 `tests/` 时，仍会遇到旧
Occupational Core-6 的 `TaskRegistry` 预期。验证旧路径时，请把任务目录切到
`tasks/_archive_openclaw_core6/`。

## Git 约定

- `.gitignore` 中必须使用 `/RedDust/` 这种锚定写法；裸写 `RedDust/` 会在大小写不敏感的 macOS 文件系统上误伤 `openclaw/reddust/`。
- 不提交生成产物：`RedDust/node_modules/`、`RedDust/dist/`、`RedDust/tsconfig.tsbuildinfo`、`runs/`、缓存、压缩包和本地 workspaces。
- 需要提交的是源码、任务规格、测试、脚本、文档，以及确实更新过的 RedDust submodule 指针。
