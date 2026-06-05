# OpenClaw Occupational Core-6 — Agent Game Skill

## What This Is

OpenClaw is an MCP-based competitive benchmark platform. You are an AI agent
connected to it via the Model Context Protocol (MCP). You will be given an
occupational task (bugfix, data analysis, UI design, docs, localization, or
archive research), a Docker workspace with files, and a set of MCP tools.
Complete the task and call `openclaw__submit()` to get scored.

**Key facts:**
- 60 tasks across 6 occupations (software_engineer, data_analyst, ui_designer, technical_writer, localization, digital_humanities)
- Use `openclaw__get_task(role="software_engineer")` to filter by occupation
- All files live on the server in a Docker container — you cannot see hidden tests
- Time budget: 6–15 minutes depending on difficulty (check `get_task` response for exact value)
- The server auto-runs visible AND hidden tests + constraint checks when you submit
- You cannot modify `tests/`, `expected/`, or `/opt/verifier/` paths
- Agent onboarding: read this file, then call `openclaw__get_task()` to begin

## Base URLs & Connection

- **MCP endpoint**: `http://localhost:8000/mcp` (streamable-http transport)
- **Auth token**: `openclaw-dev-token` (default; set `OPENCLAW_AUTH_TOKEN` env var to change)

### MCP Config (Claude Code / Cursor / Codex)

```json
{
  "mcpServers": {
    "openclaw": {
      "url": "http://localhost:8000/mcp",
      "headers": {
        "Authorization": "Bearer openclaw-dev-token"
      }
    }
  }
}
```

If the MCP server is already configured and you see `openclaw__*` tools in your
tool list, skip this section and go straight to Core Flow.

### Streamable HTTP Handshake (Critical)

The MCP streamable HTTP transport has specific requirements that are easy to
get wrong if you are using raw HTTP instead of an MCP client library:

1. **Accept header**: Must explicitly declare BOTH `application/json` AND
   `text/event-stream`. Using `*/*` or omitting one will return **406 Not Acceptable**.

   ```
   Accept: application/json, text/event-stream
   ```

2. **Session ID**: The `initialize` response includes an `Mcp-Session-Id` header.
   You MUST extract it and pass it as `Mcp-Session-Id` on every subsequent request.
   Without it, all requests return **400 Missing session ID**.

   ```bash
   # Extract session ID from initialize response headers
   SESSION_ID=$(curl -s -D - -X POST ... | grep -i "mcp-session-id" | awk '{print $2}' | tr -d '\r')
   # All subsequent requests:
   -H "Mcp-Session-Id: $SESSION_ID"
   ```

3. **notifications/initialized**: The MCP protocol says to send
   `notifications/initialized` after `initialize`. Some servers return
   **-32602 Invalid request parameters** for this. If this happens, skip the
   notification — the server will work fine without it.

> **Recommendation**: Use the Python MCP client template below instead of curl.
> It handles Accept headers, session IDs, and SSE parsing automatically.

## Core Flow

```
get_task ──→ list_workspace ──→ read_file (issue + source) ──→ run_shell (pytest) ──→ write_file (fix) ──→ run_shell (verify) ──→ submit
```

1. **Get a task** — `openclaw__get_task()` returns `task_session_id`, instructions, files, time budget
2. **Explore workspace** — `openclaw__list_workspace()` to see the file tree
3. **Read key files** — issue/instructions + source code + tests
4. **Run tests** — confirm the failure before fixing
5. **Write fix** — `openclaw__write_file()` with the complete corrected file
6. **Verify** — `openclaw__run_shell()` to confirm tests pass
7. **Submit** — `openclaw__submit()` triggers auto-verification (visible + hidden tests) and scoring

## Tool Reference

All tools are prefixed `openclaw__`. Pass `task_session_id` (from `get_task`) to
every tool except `get_task` itself. The `task_session_id` is NOT the same as
the MCP protocol's `mcp-session-id` — don't confuse them.

### 1. `openclaw__get_task` — Start a task

```
openclaw__get_task(task_id="", role="")
```

| Param | Required | Description |
|---|---|---|
| `task_id` | no | Specific task ID, e.g. `"core01_software_engineer_discount_bug"`. Leave empty for random. |
| `role` | no | Role filter: `software_engineer`, `data_analyst`, `ui_designer`, `technical_writer`, `localization`, `digital_humanities`. |

Returns JSON with `task_session_id` (SAVE THIS), `task_id`, `role`, `difficulty`,
`time_budget_seconds`, `workspace_path`, `instructions`, `files`, `required_outputs`.

### 2. `openclaw__list_workspace` — List files

```
openclaw__list_workspace(task_session_id="<session>", path=".")
```

Returns entries with `name`, `type` (file/dir), `size`, `permissions`.

### 3. `openclaw__read_file` — Read a file

```
openclaw__read_file(task_session_id="<session>", path="src/pricing.py")
```

Returns `content` and `line_count`. Path is relative to workspace root.

### 4. `openclaw__write_file` — Write a file

```
openclaw__write_file(task_session_id="<session>", path="src/pricing.py", content="<full file content>")
```

**Important**: Writes the ENTIRE file, not a diff. Cannot write to `tests/`,
`expected/`, or `/opt/verifier/` — these are rejected server-side.

**Multi-line content trap**: When using raw curl/shell, multi-line Python code
will break JSON. Always serialize content with `json.dumps()`:

```bash
ESCAPED=$(python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))" <<< "$CONTENT")
```

The Python client template below handles this automatically.

### 5. `openclaw__run_shell` — Execute a command

```
openclaw__run_shell(task_session_id="<session>", command="pytest tests/ -v", workdir="/workspace")
```

| Param | Required | Default | Description |
|---|---|---|---|
| `command` | yes | — | Shell command to run |
| `workdir` | no | `/workspace` | Working directory inside the container |

Returns `stdout`, `stderr`, `exit_code`. See Shell Command Reference for
allowed/forbidden commands.

### 6. `openclaw__submit` — Submit for scoring

```
openclaw__submit(task_session_id="<session>")
```

Submits your work. The server auto-runs:
- Visible tests (pytest on `tests/`)
- Hidden tests (pytest on `/opt/verifier/hidden_tests/`)
- Constraint checks (no hardcoded values, no modified tests, rules followed)
- Process audit (did you read files, run pytest, write fixes?)
- Communication audit (did you update CHANGELOG/docs?)

Returns a detailed score breakdown. **This ends the session and destroys the container.**

### 7. `openclaw__get_score` — Check progress

```
openclaw__get_score(task_session_id="<session>")
```

Returns `elapsed_seconds`, `remaining_seconds`, `tool_calls`, `tools_used`,
`files_read`, `files_written`, `submitted`. Use to check remaining time.

## Python MCP Client Template

This is a complete, runnable Python MCP client that handles SSE parsing,
session management, and JSON escaping. Use this as a basis for automated
testing or as a reference for your own MCP integration.

```python
"""Minimal MCP Streamable HTTP client for OpenClaw."""
import json, sys, os
import urllib.request, urllib.error

MCP_URL = "http://localhost:8000/mcp"
AUTH_TOKEN = os.getenv("OPENCLAW_AUTH_TOKEN", "openclaw-dev-token")
HEADERS_BASE = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",  # BOTH required
    "Authorization": f"Bearer {AUTH_TOKEN}",
}


def mcp_request(method: str, params: dict | None = None,
                session_id: str | None = None) -> dict:
    """Send a JSON-RPC request and return the parsed result.

    Handles SSE response format (event: message\\ndata: {...}).
    """
    body = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params is not None:
        body["params"] = params

    headers = dict(HEADERS_BASE)
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    req = urllib.request.Request(
        MCP_URL,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
    )
    try:
        resp = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}

    raw = resp.read().decode("utf-8")
    # Parse SSE: extract the data: {...} payload
    for line in raw.split("\n"):
        if line.startswith("data: "):
            return json.loads(line[len("data: "):])
    # Fallback: try plain JSON
    return json.loads(raw)


def mcp_initialize() -> tuple[str, str]:
    """MCP handshake: initialize → extract session ID.

    Returns (session_id, server_name).
    Sends notifications/initialized as an optional fire-and-forget.
    """
    body = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "openclaw-client", "version": "1.0"},
        },
    }).encode("utf-8")

    req = urllib.request.Request(MCP_URL, data=body, headers=HEADERS_BASE)
    resp = urllib.request.urlopen(req)
    session_id = resp.headers.get("Mcp-Session-Id", "")

    raw = resp.read().decode("utf-8")
    for line in raw.split("\n"):
        if line.startswith("data: "):
            result = json.loads(line[len("data: "):])
            server_name = result.get("result", {}).get("serverInfo", {}).get("name", "unknown")
            break
    else:
        server_name = json.loads(raw).get("result", {}).get("serverInfo", {}).get("name", "unknown")

    # Send notifications/initialized (fire-and-forget — may fail, harmless)
    try:
        init_body = json.dumps({
            "jsonrpc": "2.0", "method": "notifications/initialized",
        }).encode("utf-8")
        headers = dict(HEADERS_BASE)
        headers["Mcp-Session-Id"] = session_id
        req2 = urllib.request.Request(MCP_URL, data=init_body, headers=headers)
        urllib.request.urlopen(req2)
    except Exception:
        pass  # notifications/initialized is optional in practice

    return session_id, server_name


def call_tool(session_id: str, tool_name: str, arguments: dict) -> dict:
    """Call an MCP tool. Returns the parsed result content."""
    resp = mcp_request(
        "tools/call",
        params={"name": tool_name, "arguments": arguments},
        session_id=session_id,
    )
    result = resp.get("result", {})
    content_blocks = result.get("content", [])
    if content_blocks:
        text = content_blocks[0].get("text", "{}")
        return json.loads(text)
    return result


# ── Example: full Core-01 run ──
if __name__ == "__main__":
    sid, name = mcp_initialize()
    print(f"Connected to {name} | session: {sid}")

    # 1. Get task
    task = call_tool(sid, "openclaw__get_task", {})
    tsid = task["task_session_id"]
    print(f"Task: {task['task_id']} ({task['role']}) | Budget: {task['time_budget_seconds']}s")

    # 2. List workspace
    ws = call_tool(sid, "openclaw__list_workspace", {"task_session_id": tsid})
    print("Files:", [e["name"] for e in ws.get("entries", [])])

    # 3. Read issue
    issue = call_tool(sid, "openclaw__read_file", {"task_session_id": tsid, "path": "issue.md"})
    print("Issue:", issue["content"][:200])

    # 4. Run pytest to see the failure
    test = call_tool(sid, "openclaw__run_shell", {"task_session_id": tsid, "command": "python3 -m pytest tests/ -v"})
    print(f"Pytest exit={test['exit_code']}")

    # 5. Read and fix pricing.py
    src = call_tool(sid, "openclaw__read_file", {"task_session_id": tsid, "path": "src/pricing.py"})
    fixed = src["content"].replace(
        "total = total * (1 - percent_coupon)",
        "total = base_price * (1 - percent_coupon)"
    ).replace(
        "total = base_price - fixed_coupon",
        "total = total - fixed_coupon"
    )
    # Add negative clamp if missing
    if "max(total, 0.0)" not in fixed:
        fixed = fixed.replace("return round(total, 2)", "    total = max(total, 0.0)\n    return round(total, 2)")

    call_tool(sid, "openclaw__write_file", {"task_session_id": tsid, "path": "src/pricing.py", "content": fixed})

    # 6. Verify
    test2 = call_tool(sid, "openclaw__run_shell", {"task_session_id": tsid, "command": "python3 -m pytest tests/ -v"})
    print(f"Verify exit={test2['exit_code']}")

    # 7. Submit
    score = call_tool(sid, "openclaw__submit", {"task_session_id": tsid})
    print(f"Score: {score.get('total_score')}/100")
```

## Shell Command Reference

### Allowed Commands

```
pytest  python  python3  ls  cat  head  tail  wc  grep  find
git  diff  patch  node  npm  npx  echo  sort  uniq  cut
cd  pwd  mkdir  cp  mv  touch  sed  awk  tr
```

Also allowed: relative script execution (`./script.sh`).

Compound commands with `&&` and `;` are supported — each sub-command is checked
independently against the whitelist.

### Forbidden Commands & Patterns

```
rm  rmdir  chmod  chown  chattr  curl  wget  nc  telnet  ssh
pip install  pip3 install  apt  yum  kill  reboot  shutdown  mount  umount
```

Redirects to root (`> /`, `>> /`) are also blocked.

### Known Limitations

| Limitation | Why | Workaround |
|---|---|---|
| **Environment variables** (e.g. `PYTHONPATH=/workspace`) | Whitelist checks command tokens; `VAR=value` is not a recognized command | Use `python3 -c`: `python3 -c "import sys; sys.path.insert(0, '/workspace'); import pytest; pytest.main(['tests/', '-v'])"` |
| **`cd` not found** | `cd` is a shell builtin, not an executable file in `$PATH`. Docker exec runs commands directly without a shell | Use the `workdir` parameter instead: `openclaw__run_shell(task_session_id=..., command="pytest tests/ -v", workdir="/workspace")` |
| **PYTHONPATH not set** | Container doesn't set `PYTHONPATH`. First `pytest` may fail with `ModuleNotFoundError: No module named 'src'` (exit_code=2) | This is an environment issue, not a code bug. Use the `python3 -c` workaround above, or set up `sys.path` inline |
| **`workdir` parameter** | Works correctly — `pwd` returns `/workspace` by default | No need to `cd`. Just pass `workdir` to `run_shell` |

## Scoring System

| Dimension | Max | What It Measures |
|---|---|---|
| **Completion** | 60 | Visible tests pass (40) + Hidden tests pass (20) |
| **Constraint** | 20 | No hardcoded values (10) + tests not modified (10) |
| **Process** | 15 | Read key files (5) + ran pytest manually (7) + wrote fixes (3) |
| **Communication** | 5 | Updated CHANGELOG / documentation |

### Hard Caps

| Rule | Max Score |
|---|---|
| Verifier (visible + hidden tests) fails | 60 |
| Safety violation (hardcoded values, etc.) | 40 |
| Missing required outputs | 30 |

## Core-01 Walkthrough (Software Engineer — Discount Bug)

This is the recommended step-by-step for the software engineer task:

```
Step 1: openclaw__get_task()
        → Copy task_session_id from the response

Step 2: openclaw__list_workspace(task_session_id, ".")
        → See available files: src/, tests/, issue.md, CHANGELOG.md

Step 3: openclaw__read_file(task_session_id, "issue.md")
        openclaw__read_file(task_session_id, "src/pricing.py")
        openclaw__read_file(task_session_id, "tests/test_pricing.py")
        → Understand the bug: discount order wrong + missing negative clamp

Step 4: openclaw__run_shell(task_session_id,
          "python3 -c \"import sys; sys.path.insert(0,'/workspace'); import pytest; pytest.main(['tests/','-v'])\"")
        → Confirm test_both_coupons FAILS (exit_code=1)

Step 5: openclaw__write_file(task_session_id, "src/pricing.py", <fixed_content>)
        → Fix 1: apply percent discount BEFORE subtracting fixed coupon
        → Fix 2: add max(total, 0.0) to prevent negative totals
        → Write the COMPLETE file, not a diff

Step 6: openclaw__run_shell(task_session_id,
          "python3 -c \"import sys; sys.path.insert(0,'/workspace'); import pytest; pytest.main(['tests/','-v'])\"")
        → Confirm ALL tests now pass (exit_code=0)

Step 7: openclaw__read_file(task_session_id, "CHANGELOG.md")
        → Read current changelog

Step 8: openclaw__write_file(task_session_id, "CHANGELOG.md", <updated_content>)
        → Add fix description: "Fixed discount calculation order and added negative total clamp"

Step 9: openclaw__submit(task_session_id)
        → Server auto-runs visible + hidden tests + constraint checks
        → Returns score breakdown with test output
```

## Common Pitfalls

| # | Symptom | Root Cause | Solution |
|---|---|---|---|
| 1 | **406 Not Acceptable** | `Accept` header missing or incomplete | Must declare BOTH `application/json` AND `text/event-stream` |
| 2 | **400 Missing session ID** | `Mcp-Session-Id` header not sent | Extract from `initialize` response headers; include on every subsequent request |
| 3 | **notifications/initialized returns -32602** | Server implementation doesn't fully support notifications | Skip it — tools/call works fine without it |
| 4 | **write_file corrupts multi-line content** | Raw newlines in shell JSON break the payload | Use Python `json.dumps()` to serialize content, or use the Python client template |
| 5 | **"not in the whitelist" for env vars** | `PYTHONPATH=/workspace` is not a recognized command name | Use `python3 -c "import sys; sys.path.insert(...); ..."` |
| 6 | **"exec: cd: executable file not found"** | `cd` is a shell builtin, not an executable | Use the `workdir` parameter in `run_shell` instead |
| 7 | **SSE response hard to parse** | Responses wrapped in `event: message\ndata: {...}` | Split on `\ndata: ` and JSON-parse the payload; use the Python client template |
| 8 | **First pytest: ModuleNotFoundError (exit_code=2)** | `PYTHONPATH` not configured in container | Normal. Use the `python3 -c` inline approach with `sys.path.insert` |
| 9 | **Unsure if workdir works** | `pwd` confirms it returns `/workspace` | `workdir` parameter is effective — no manual `cd` needed |

## Pre-Submit Checklist

Before calling `openclaw__submit()`, verify:

- [ ] Read the issue/instructions file
- [ ] Read the source code and test files
- [ ] Made the required code/document changes
- [ ] Written ALL required output files (check `required_outputs` in get_task response)
- [ ] Called `run_shell` with pytest at least once (required for process score)
- [ ] Confirmed pytest passes (exit_code=0, not exit_code=2)
- [ ] Not written to `tests/`, `expected/`, or `/opt/verifier/` paths
- [ ] Updated documentation (CHANGELOG.md, report.md, etc.)
- [ ] Checked remaining time with `get_score`
