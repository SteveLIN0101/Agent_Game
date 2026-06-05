# CLAUDE.md — OpenClaw Agent Game

## Current Project Overview

OpenClaw Agent Game is currently centered on the **Red Dust Readable-by-Design**
task set: 60 SHELTER/Red Dust tasks that convert WildClaw-style occupational
capabilities into visible survival-world actions, state changes, replay beats,
and automatic scoring.

For Claude, this file is the project-level memory/instruction entry. For the
repository's own design-discussion memory, also read
`docs/design-discussion/Memory.md`.

The earlier **OpenClaw Occupational Core-6** MCP benchmark is archived, not
deleted, under `tasks/_archive_openclaw_core6/`.

## Environment

- **Python**: `/Users/steve/miniconda3/envs/agent_game/bin/python` (conda env `agent_game`, Python 3.13.13)
- **Working directory**: `/Users/steve/Documents/2026Spring/Agent_Game`
- **Default tests**: `PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python -m pytest tests/ -v`
- **Red Dust focused tests**: `PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python -m pytest tests/test_reddust_deeplib.py tests/test_reddust_deep_remaining.py tests/test_reddust_all60.py -q`
- **Archived Core-6 tests**: `OPENCLAW_TASKS_DIR="$PWD/tasks/_archive_openclaw_core6" PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python -m pytest tests/ -q`
- **Start legacy MCP server**: `PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python -m openclaw.mcp_server`
- **Legacy MCP endpoint**: `http://localhost:8000/mcp` (streamable-http mode)
- **Auth token**: `openclaw-dev-token` (default, configurable via `OPENCLAW_AUTH_TOKEN`)
- **External OpenClaw agent smoke test**: `openclaw agent --agent main -m hello`
- **External OpenClaw agent context clear**: `openclaw agent --agent main -m /clear`

## Key Files

| File | Purpose |
|---|---|
| `AGENTS.md` | Codex-facing first project memory/instructions |
| `CLAUDE.md` | Claude-facing project memory/instructions |
| `docs/design-discussion/Memory.md` | Repository design-discussion memory |
| `docs/design-discussion/Progress.md` | Design-discussion progress log |
| `red_dust_readable_task_conversion.html` | Source report for Red Dust readable conversion |
| `tasks/RED_DUST_INDEX.md` | Human-readable index for all 60 Red Dust tasks |
| `tasks/rd_*` | Default 60 Red Dust readable tasks |
| `tasks/_archive_openclaw_core6/` | Archived 60 Occupational Core-6 tasks |
| `openclaw/reddust/` | Red Dust runtime, scoring, bridge, perception, generic/deep graders |
| `openclaw/reddust/deeplib.py` | Shared family deep-grading harnesses |
| `openclaw/reddust/generic.py` | Generic scaffold library retained for regression tests; no default task uses it now |
| `openclaw/reddust/agent_bridge.py` | JSON-action bridge for external chat agents |
| `scripts/openclaw_agent_runner.py` | Runs live `openclaw agent` against a Red Dust task |
| `scripts/run_reddust_live_openclaw_batch.py` | Runs all Red Dust tasks through live `openclaw agent` and renders an HTML report |
| `scripts/generate_red_dust_tasks.py` | Regenerates readable task specs from the HTML report |
| `scripts/generate_reddust_runnable.py` | Generates generic runnable shims |
| `scripts/bind_deep_family.py` | Binds tasks to shared deep-grading families |
| `scripts/author_deep_remaining.py` | Idempotently authors/binds the final 21 tasks to deep families |
| `openclaw/mcp_server.py` | Legacy FastMCP server with 7 tools |
| `openclaw/task_registry.py` | Legacy occupational YAML task loader |

## Red Dust Readable-Task Conversion (2026-05-31)

**The default `tasks/` directory now holds the 60 Red Dust Readable-by-Design
tasks** generated from `red_dust_readable_task_conversion.html` (§6 cards + §7
spec samples).

- **60 tasks** across 6 readable categories: Productivity Flow 10 · Code Intelligence 12 · Social Interaction 6 · Search & Retrieval 11 · Creative Synthesis 11 · Safety Alignment 10.
- **Per-task readable format**: `task.yaml` (`user_visible_goal`, `visible_state`, `available_tools`, `critical_beats_for_replay`, `success_checks`, `visible_result_card`, provenance) plus `card.md`.
- **Readable index**: `tasks/RED_DUST_INDEX.md` documents the 7 gates, 8 visual tool/action classes, 6 category principles, and full 60-task table.
- **Generator**: `scripts/generate_red_dust_tasks.py` parses the HTML report and validates every YAML spec.
- **Archived old benchmark**: the former 60 Occupational Core-6 tasks are in `tasks/_archive_openclaw_core6/` and remain runnable via `OPENCLAW_TASKS_DIR`.
- **Known impact**: `TaskRegistry`/`TaskRole`/`tests/test_task_registry.py` still target the old occupational schema. Against the default Red Dust `tasks/`, the 6 old registry tests fail because the registry skips the new §7 tasks; against the archive, they pass.

## Red Dust Runtime + Grading Status

The Red Dust execution layer lives in `openclaw/reddust/`:

- `world.py`: visible world state, loaded inputs, replay events, artifacts.
- `checks.py`: `Check` assertion objects.
- `scoring.py`: weighted 0-100 score, critical hard cap at 40, at most 3 readable failure reasons.
- `engine.py`: `run_solution` pure core and `run_task_dir` disk loader.
- `agent_bridge.py`: external chat-agent JSON action protocol.
- `perception.py`: text/perception tools for non-multimodal agents.
- `generic.py`: baseline trajectory/output-conformance scaffold retained for tests/history.
- `deeplib.py`: shared family deep graders that grade against per-task `inputs/data.json` and `expected/key.json`.

Current runnable/scoring coverage:

- **All 60 tasks are runnable + auto-scored**.
- **58 tasks** are bound to shared family deep graders:
  - `build`: 14
  - `code`: 1
  - `jigsaw`: 2
  - `puzzle`: 4
  - `search`: 13
  - `classify`: 8
  - `schedule`: 1
  - `safety`: 10
  - `report`: 5
- **2 tasks** have bespoke deep graders:
  - `rd_si_01_water_run_negotiation`
  - `rd_ci_03_escape_map_jigsaw_3x3`
- **0 tasks** use the generic scaffold. The final 21 former scaffold tasks were upgraded via `scripts/author_deep_remaining.py`.
- `tests/test_reddust_all60.py` asserts every task's `gold` score is at least 85 and beats `bad` by at least 30.

## External OpenClaw Agent Bridge

`scripts/openclaw_agent_runner.py` lets the globally installed `openclaw` CLI
solve a Red Dust task through `openclaw/reddust/agent_bridge.py`:

```bash
openclaw agent --agent main -m hello
python scripts/openclaw_agent_runner.py tasks/rd_si_01_water_run_negotiation --max-steps 12
PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python \
  scripts/run_reddust_live_openclaw_batch.py --max-steps 12 --timeout 160 \
  --smoke --clear-before --clear-after
openclaw agent --agent main -m /clear
```

Observed status:

- The `openclaw` CLI is a separate installed product, not this repo's legacy `python -m openclaw.mcp_server`.
- Gateway scope approval is currently pending; the CLI falls back to embedded mode.
- Latest full live batch (2026-06-01): **60/60 tasks executed**, **58/60 submitted**, **15/60 passed_all**, average score **63.27**, **401** total agent turns, accumulated task duration **7696.7s**.
- Latest HTML report: `runs/reddust_live_openclaw_20260601_013937/report.html`; per-task JSON logs are in `runs/reddust_live_openclaw_20260601_013937/tasks/`.
- Category pass counts from that run: CI 6/12 · CS 0/11 · PF 0/10 · SA 7/10 · SI 0/6 · SR 2/11.
- Not submitted in that run: RD-CI-03 (visual jigsaw exhausted perception steps) and RD-SI-01 (scored 94.7 but hit max steps before `submit`).

## Perception Layer

The live agent path is text-first, so visual tasks rely on perception tools in
`openclaw/reddust/perception.py`:

- `ocr_text`, `ocr_digit_with_rotation`, `read_tile`, `describe_image`.
- Chinese OCR data `chi_sim.traineddata` is available in `/opt/homebrew/share/tessdata/`.
- RD-CI-03 is solvable from perception alone via `solutions/perception_gold.py` and scores 100/100 in the tested environment.
- Heavy document extraction (MinerU/PaddleOCR) is still an on-demand future path for PDF/table-heavy tasks.

## Verification Snapshot (2026-06-01)

Already verified in conda env `agent_game`:

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
# The 6 failures are the old TaskRegistry tests expecting occupational-schema tasks.

OPENCLAW_TASKS_DIR="$PWD/tasks/_archive_openclaw_core6" \
  PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python -m pytest tests/ -q
# 187 passed

PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python -m pytest \
  tests/test_reddust_bridge.py tests/test_reddust_all60.py -q
# 68 passed
```

## Legacy MCP Tools (v1.1)

These belong to the archived Occupational Core-6 path:

| Tool | Key Parameter |
|---|---|
| `openclaw__get_task` | — returns `task_session_id` |
| `openclaw__list_workspace` | `task_session_id`, `path` |
| `openclaw__read_file` | `task_session_id`, `path` |
| `openclaw__write_file` | `task_session_id`, `path`, `content` |
| `openclaw__run_shell` | `task_session_id`, `command`, `workdir` |
| `openclaw__submit` | `task_session_id` — auto-runs visible + hidden tests |
| `openclaw__get_score` | `task_session_id` — progress check |

## Legacy Occupational Core-6 History

- **Phase 2 (2026-05-10)**: created 60 occupational tasks (10 per occupation × 6 occupations), each with inputs, tests, hidden tests, and verifier.
- **Difficulty distribution**: 4 easy + 4 medium + 2 hard per occupation, except software_engineer 4+5+1.
- **571 files** across old task directories.
- **Docker images**: Dockerfile.core02 through core06 extend `openclaw-base`.
- **Role-agnostic scoring**: `openclaw/scoring.py` handles arbitrary `verify_output` keys.
- **v1.1/v1.2 usability work**: shell whitelist expansion, `task_session_id`, bearer token auth, visible/hidden submit output, `openclaw_game.skill.md`, HTML implementation guide updates.

## Current Gaps / Next Work

- Analyze the 2026-06-01 live batch failures and decide which are agent limits vs bridge/tool-catalog UX issues.
- Decide whether and how to wire Red Dust tasks into the legacy MCP/Docker sandbox path.
- Improve true multimodal live-agent evaluation for visual tasks beyond the current text/perception bridge.

## 2026-06-05 · Cleanup Note (RedDust sub-project)

The project root is **not a git repo**; deletion is not recoverable. The 2026-06-05 cleanup deleted only rebuildable artifacts and zip files whose decompressed form was already on disk:

- **Deleted (Tier 1, rebuildable)**: `.DS_Store`, `.pytest_cache`, 184 `__pycache__` (≈1.8M), `RedDust/node_modules/` (232M), `RedDust/dist/` (30M), `RedDust/tsconfig.tsbuildinfo`, `agent-survival-game/.godot/` (120M).
- **Deleted (Tier 2, decompressed siblings exist)**: `agent-survival-game.zip` (329M), `openclaw_core6_team_sync.tar.gz` (20M), `openclaw_core6_team_sync/archives/`, `素材/red-dust-character-states-en.zip` (33M), two Godot asset zips in `agent-survival-game/data/` (61M+14M).
- **Backed up to `~/Downloads/Agent_Game_Backup/` (369M, byte-identical)**: the three non-rebuildable large items (`agent-survival-game.zip`, `openclaw_core6_team_sync.tar.gz`, `openclaw_core6_team_sync/archives/`).
- **Kept untouched**: `openclaw_core6_team_sync/` (114M, current Core-6 sync source), `runs/reddust_live_openclaw_20260601_013937/`, `runs/reddust_live_openclaw_v2_modified_20260601/`, `runs/reddust_lan_sessions/`, all 60 `tasks/rd_*`, `openclaw/reddust/`, `tests/`, `scripts/`, `docs/`, `red_dust_readable_task_conversion.html`, `tasks/_archive_openclaw_core6/`.
- **Result**: project root went from ≈810M to ≈430M (≈380M freed); `tests/test_reddust_deeplib.py tests/test_reddust_deep_remaining.py tests/test_reddust_all60.py -q` still 117 passed.
- **Note for downstream**: `RedDust/` no longer contains `node_modules`/`dist`/`tsconfig.tsbuildinfo`; rebuild with `npm install && npm run build` in that sub-directory.

## 2026-06-05 · Git Init + RedDust Submodule

The project root was initialized as a git repository and the first commits were pushed to GitHub on 2026-06-05.

- **Parent remote**: `https://github.com/SteveLIN0101/Agent_Game.git` (private, default branch `main`).
- **First commit `f4b7bed`**: "Initial import: OpenClaw Agent Game / Red Dust benchmark" — 2698 files, `.git` 130M (transmitted as ≈116M pack).
- **Submodule pointer commit `fb9bb1c`**: "Add RedDust as git submodule (pinned to agent-game-integration @ c49f17d)".
- **RedDust submodule**: `https://github.com/peter-cui-yi/RedDust.git` at `RedDust/`, pinned to `c49f17d` on the `agent-game-integration` branch.
  - The `agent-game-integration` branch exists **only locally** in this checkout; it carries the local campaign integration changes (README, App, AgentControlBar, global styles + new `campaignClient.ts` / `campaignAdapter.ts`) that were uncommitted on `main` before this session.
  - Per the user's decision, the RedDust origin (`peter-cui-yi/RedDust.git`) is **untouched** — the new branch is not pushed.
- **`.gitignore`**: pre-existing 145-line file already excludes `RedDust/`, `runs/`, `workspaces/`, `openclaw_core6_team_sync/`, `素材/`, `*.zip`, `*.tar.gz`, `node_modules/`, `__pycache__/`, `.godot/`, `*.tsbuildinfo` and many more. Unchanged in this round.
- **Push note**: first push failed with `curl 55 Recv failure: Connection reset by peer` because of the 130M pack; retry with `GIT_HTTP_LOW_SPEED_LIMIT=1000 GIT_HTTP_LOW_SPEED_TIME=300` succeeded.

### Clone commands

```bash
git clone https://github.com/SteveLIN0101/Agent_Game.git
cd Agent_Game
git submodule update --init --recursive
```

### Future work (submodule-related)

- Decide whether to push `agent-game-integration` to a SteveLIN0101 fork of RedDust and update the submodule pointer to a public commit.
- Consider Git LFS for the large PNG assets under `agent-survival-game/data/`.
- Add CI for RedDust + the parent benchmark separately.
