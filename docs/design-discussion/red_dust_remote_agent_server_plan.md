# Red Dust Remote Agent Server 计划

## 摘要

目标是把现有 OpenClaw / Red Dust agent 游戏整理成一个可供远程 agent 接入的环境服务。第一阶段只做同一 Wi-Fi 下的本机联调：开发机启动 Red Dust LAN server，另一台电脑上的 OpenClaw、Hermes、Claude Code、Codex、opencode 或浏览器 agent 通过 HTTP/网页入口提交 JSON action、接收 observation、最后 submit 得分并导出 trace report。

本设计不让 agent 直接访问 Python 对象、数据库或任务文件。远程 agent 只能调用公开 action；服务端负责加载任务、执行工具、记录轨迹、运行 verifier 和返回 score。

## 当前基础

现有 Red Dust runtime 已经具备远程化所需核心边界：

- `openclaw/reddust/world.py` 维护可见状态、artifacts、security log 和 replay events。
- `openclaw/reddust/engine.py` 能加载 `tasks/rd_*`、执行 gold/bad solution 并评分。
- `openclaw/reddust/agent_bridge.py` 已定义外部 agent 的 JSON action 协议：`{"tool": "...", "args": {...}}`。
- `scripts/run_reddust_live_openclaw_batch.py` 已证明 live `openclaw agent` 可用同一协议跑完整任务并生成 HTML report。

因此 V0 不重写游戏核心，而是在 Red Dust runtime 外包一层 LAN HTTP server。

## V0 架构

```text
Remote Agents
  OpenClaw / Hermes / Claude Code / Codex / opencode / browser agents
        |
        v
Red Dust LAN Server
  REST API / debug HTML / skill.md / OpenAPI-like schema
        |
        v
Existing Red Dust Core
  task.yaml / inputs / tools.py / verifier / scoring / replay
        |
        v
runs/reddust_lan_sessions/<session_id>/
  session.json / report.html
```

第一阶段不做公网部署，不把 MCP 当唯一入口。REST 是最小共同接口；MCP、WebSocket 和正式前端可作为后续 adapter 叠加。

## V0 HTTP 接口

基础接口：

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

## 同 Wi-Fi 联调步骤

开发机启动：

```bash
PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python \
  scripts/run_reddust_lan_server.py --host 0.0.0.0 --port 7000
```

开发机查看局域网 IP：

```bash
ipconfig getifaddr en0
```

另一台同 Wi-Fi 电脑 smoke：

```bash
curl http://<开发机IP>:7000/health
curl http://<开发机IP>:7000/tasks
```

创建并执行一个任务：

```bash
curl -X POST http://<开发机IP>:7000/sessions \
  -H 'Content-Type: application/json' \
  -d '{"task_id":"RD-SR-11","agent_id":"wifi-smoke","max_steps":8}'
```

浏览器 agent 可打开：

```text
http://<开发机IP>:7000/game/<session_id>
```

## 安全边界

- V0 默认面向可信局域网，不提供公网安全保证。
- 如需简单 token，可启动时传 `--auth-token <token>` 或设置 `RED_DUST_AUTH_TOKEN`。
- agent 只能调用当前任务 `tools.py` 暴露的工具名和参数，不能访问任意文件、shell、Python 对象或 hidden verifier。
- 服务端记录每个 action、observation、state、score 和 failure reasons，便于复盘。

## 后续服务器化

同 Wi-Fi 跑通后再做：

- Caddy/Nginx 反代：`/api`、`/game`、`/skill.md`、`/mcp`。
- MCP adapter：把 `start_task/get_brief/take_action/submit/get_score/get_trace` 包成 MCP tools。
- WebSocket adapter：适配长连接 agent 和实时前端 replay。
- 多租户隔离：session token、rate limit、run retention、任务白名单、只读静态资源。
- 汇总报告：把多个 session 聚合成 batch report 和 agent 对比表。

## 验收标准

- 本机测试能通过 `/health`、创建 session、执行 action、submit、读取 trace 和 HTML report。
- 另一台同 Wi-Fi 电脑能访问 `/health` 和 `/tasks`。
- 远程 agent 使用 HTTP action loop 至少能跑完一个 Red Dust 任务。
- 不破坏现有 Red Dust 60 任务 gold/bad 回归。
