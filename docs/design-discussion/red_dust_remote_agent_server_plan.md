# Red Dust Remote Agent Server 计划

## 摘要

目标是把现有 OpenClaw / Red Dust agent 游戏整理成一个可供远程 agent 接入的环境服务。当前服务同时支持单题 session 和 Day0-12 campaign：开发机启动 Red Dust LAN server，另一台电脑上的 OpenClaw、Hermes、Claude Code、Codex、opencode 或浏览器 agent 通过 HTTP/网页入口提交 JSON action、接收 observation、最后 submit 得分并导出 trace report。

本设计不让 agent 直接访问 Python 对象、数据库或任务文件。远程 agent 只能调用公开 action；服务端负责加载任务、执行工具、记录轨迹、运行 verifier 和返回 score。

## 当前基础

现有 Red Dust runtime 已经具备远程化所需核心边界：

- `openclaw/reddust/world.py` 维护可见状态、artifacts、security log 和 replay events。
- `openclaw/reddust/engine.py` 能加载 `tasks/rd_*`、执行 gold/bad solution 并评分。
- `openclaw/reddust/agent_bridge.py` 已定义外部 agent 的 JSON action 协议：`{"tool": "...", "args": {...}}`。
- `scripts/run_reddust_live_openclaw_batch.py` 已证明 live `openclaw agent` 可用同一协议跑完整任务并生成 HTML report。

因此服务不重写游戏核心，而是在 Red Dust runtime 外包一层 LAN HTTP server；campaign middleware 再把单题 session 串成完整 Day0-12 游戏。

## V0 架构

```text
Remote Agents
  OpenClaw / Hermes / Claude Code / Codex / opencode / browser agents
        |
        v
Red Dust LAN Server
  REST API / debug HTML / skill.md / OpenAPI-like schema / campaign API
        |
        v
Existing Red Dust Core
  task.yaml / inputs / tools.py / verifier / scoring / replay
        |
        v
runs/
  reddust_lan_sessions/<session_id>/session.json + report.html
  reddust_campaigns/<campaign_id>/campaign.json + report.html
```

第一阶段不做公网部署，不把 MCP 当唯一入口。REST 是最小共同接口；MCP、WebSocket 和更细粒度前端动画 adapter 可作为后续叠加。

## V0 HTTP 接口

### 单题 session 接口

- `GET /health`
- `GET /tasks`
- `GET /tasks/{task_id_or_slug}`
- `POST /sessions`
- `GET /sessions/{session_id}/brief`
- `GET /sessions/{session_id}/state`
- `POST /sessions/{session_id}/actions`
- `POST /sessions/{session_id}/submit`
- `GET /sessions/{session_id}/score`
- `GET /sessions/{session_id}/trace`
- `GET /sessions/{session_id}/report.html`
- `GET /game/{session_id}`
- `GET /skill.md`
- `GET /openapi.json`

创建 session：

```json
{
  "task_id": "RD-SI-01",
  "agent_id": "codex-lan-smoke",
  "model_id": "manual",
  "max_steps": 16
}
```

执行 action：

```json
{
  "tool": "write_conclusion",
  "args": {
    "answer": "llama-run",
    "evidence": ["d1", "clue"]
  }
}
```

服务返回 observation、剩余步数、当前可见状态和是否已经 done。`submit` 后返回 score、checks、failure reasons、trajectory 和 report URL。

### Day0-12 campaign 接口

Campaign 默认 `story_version=red_dust_readable_v1`，由 `openclaw/reddust/story_manifest.py` 提供：

- Day0：序章 `story_event`，不创建普通 task session。
- Day1-11：44 个 `Dxx-Txx` 普通任务槽，每槽按 seed 从一个或多个 `RD-*` 抽题。
- Day8-10：按 `routeLeaning=rescue|lighthouse|contested` 插入 `branch_scene`。
- Day12：Final Audit，自动结算五类结局，不使用 LLM-as-judge。

Campaign REST：

- `POST /campaigns`
- `GET /campaigns/{campaign_id}/state`
- `GET /campaigns/{campaign_id}/brief`
- `POST /campaigns/{campaign_id}/connect`
- `POST /campaigns/{campaign_id}/start`
- `GET /campaigns/{campaign_id}/events?after=0`
- `POST /campaigns/{campaign_id}/actions`
- `POST /campaigns/{campaign_id}/submit`
- `POST /campaigns/{campaign_id}/advance`
- `GET /campaigns/{campaign_id}/trace`
- `GET /campaigns/{campaign_id}/report.html`

创建 campaign：

```json
{
  "seed": "20260606-smoke",
  "story_version": "red_dust_readable_v1",
  "branch_policy": "auto",
  "task_selection": "random",
  "wait_for_start": true
}
```

事件流包含：

- `campaign_created`
- `agent_connected`
- `campaign_started`
- `story_event`
- `task_started`
- `action_executed`
- `task_submitted`
- `slot_completed`
- `day_changed`
- `branch_decided`
- `branch_scene`
- `final_audit`
- `campaign_complete`

`trace` 会返回 `frontend_trace`，每步含 `state_before`、`state_after`、`phase_hint` 和 `frontend_task`，前端 replay 可在不重跑 agent 的情况下 Step/Back/Auto Play。

## 同 Wi-Fi 联调步骤

开发机启动：

```bash
PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python \
  scripts/run_reddust_lan_server.py --host 0.0.0.0 --port 7001
```

开发机查看局域网 IP：

```bash
ipconfig getifaddr en0
```

另一台同 Wi-Fi 电脑 smoke：

```bash
curl http://<开发机IP>:7001/health
curl http://<开发机IP>:7001/tasks
```

创建并执行一个任务：

```bash
curl -X POST http://<开发机IP>:7001/sessions \
  -H 'Content-Type: application/json' \
  -d '{"task_id":"RD-SR-11","agent_id":"wifi-smoke","max_steps":8}'
```

浏览器 agent 可打开：

```text
http://<开发机IP>:7001/game/<session_id>
```

Campaign smoke：

```bash
curl -X POST http://<开发机IP>:7001/campaigns \
  -H 'Content-Type: application/json' \
  -d '{"seed":"wifi-smoke","story_version":"red_dust_readable_v1","branch_policy":"auto","task_selection":"first"}'
```

OpenClaw runner：

```bash
PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python \
  scripts/run_reddust_campaign_agent.py \
  --base-url http://<开发机IP>:7001 \
  --story-version red_dust_readable_v1 \
  --branch-policy auto \
  --connect-agent
```

前端 live/replay：

```text
http://<开发机IP>:5176/?mode=live&api=http://<开发机IP>:7001
http://<开发机IP>:5176/?mode=replay&api=http://<开发机IP>:7001&campaign_id=rdcamp-...
```

## 安全边界

- V0 默认面向可信局域网，不提供公网安全保证。
- 如需简单 token，可启动时传 `--auth-token <token>` 或设置 `RED_DUST_AUTH_TOKEN`。
- agent 只能调用当前任务 `tools.py` 暴露的工具名和参数，不能访问任意文件、shell、Python 对象或 hidden verifier。
- 服务端记录每个 action、observation、state、score 和 failure reasons，便于复盘。
- `wait_for_start=true` 的 campaign 在前端点击 Start 前会阻塞 action/submit，便于现场演示时先完成 agent 连接提示。

## 后续服务器化

同 Wi-Fi 跑通后再做：

- Caddy/Nginx 反代：`/api`、`/game`、`/skill.md`、`/mcp`。
- MCP adapter：把 `start_task/get_brief/take_action/submit/get_score/get_trace` 包成 MCP tools。
- WebSocket adapter：适配长连接 agent 和实时前端 replay。
- 多租户隔离：session token、rate limit、run retention、任务白名单、只读静态资源。
- 汇总报告：把多个 campaign/session 聚合成 batch report、agent 对比表和论文实验表。

## 验收标准

- 本机测试能通过 `/health`、创建 session、执行 action、submit、读取 trace 和 HTML report。
- Campaign 测试能通过 `/campaigns`、`/connect`、`/start`、`/events`、`/trace` 和 `/report.html`。
- 另一台同 Wi-Fi 电脑能访问 `/health` 和 `/tasks`。
- 远程 agent 使用 HTTP action loop 至少能跑完一个 Red Dust 任务，并能完整跑完一轮 Day0-12 campaign。
- 不破坏现有 Red Dust 60 任务 gold/bad 回归。
