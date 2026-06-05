# Red Dust runtime — execution + auto-scoring for §7 readable tasks

This package turns a Red Dust `tasks/rd_*` **readable spec** into something that
can actually run an agent's solution and **auto-score** it.

```
openclaw/reddust/
  world.py     World: live visible_state + static inputs + replay trajectory + artifacts
  checks.py    Check: one grader assertion (passed/weight/hidden/critical/fail_reason)
  scoring.py   score_checks(): weighted 0–100 + hard caps + ≤3 readable failure reasons (G6)
  engine.py    run_solution() (pure) / run_task_dir() (load tools+verify+solution from disk)
  story_manifest.py  Day0-12 campaign canon (red_dust_readable_v1)
  campaign.py        campaign middleware over single-task sessions
  lan_server.py      REST API for sessions, campaigns, trace, and reports
```

## What makes a task runnable

A `task.yaml` spec alone is not testable. To run + score, a task directory adds:

```
tasks/rd_xx_NN_slug/
  task.yaml              # the §7 readable spec (already generated)
  card.md                # the human-readable card (already generated)
  inputs/                # REAL task data the agent reads (*.json auto-loaded; images/etc.)
  expected/              # grader truth / answer key (*.json auto-loaded as expected_<stem>)
  tools.py               # build_tools(world) -> {name: callable}; tools mutate the World
  verifier/verify.py     # verify(world) -> list[Check]; turns success_checks into assertions
  solutions/gold.py      # solve(tools, world): a correct submission (reference) -> ~100
  solutions/bad.py       # solve(tools, world): a plausible failure mode -> critically capped
```

### Contracts

- **tools.py** → `build_tools(world)` returns a dict of callables. Each reads
  `world.inputs` and records a beat via `world.record(tool, args=, beat=, delta=)`,
  writes results with `world.set_artifact(name, value)`, and may adjust numeric
  state with `delta=`.
- **verifier/verify.py** → `verify(world)` returns `list[Check]`. Visible checks
  mirror the spec's `success_checks`; hidden checks catch trap-avoidance and
  side effects (G5). Mark a check `critical=True` when failing it is worse than
  doing nothing (opened a door, leaked water, sent 小铁 outside) — it hard-caps
  the score at 40.
- **solutions/** → `solve(tools, world)` drives the tools. `gold` should pass
  every check; `bad` encodes the failure mode the task is meant to detect. They
  are the regression test that the grader *discriminates*.

## Run it

```bash
# pretty scorecard (gold | bad | all)
python scripts/run_reddust_task.py tasks/rd_si_01_water_run_negotiation all
python scripts/run_reddust_task.py tasks/rd_ci_03_escape_map_jigsaw_3x3 gold

# programmatic
python -c "from openclaw.reddust.engine import run_task_dir; \
print(run_task_dir('tasks/rd_si_01_water_run_negotiation','gold')['score'])"

# tests (runtime primitives + the two template tasks)
PYTHONPATH=. python -m pytest tests/test_reddust_runtime.py tests/test_reddust_tasks.py -v
```

## Template tasks (done)

| Task | inputs | grader highlights |
|---|---|---|
| **RD-SI-01** 三轮取水行动协商 | note board (含假纸条), NPC 日程 (沈芷月时间矛盾), 装备表 | 不派小铁(critical) · 不用假纸条地点(critical) · 低沙暴窗口 · 真实可用时间 |
| **RD-CI-03** 3×3 逃生地图拼回去 | 15 张真实碎片 PNG + manifest, 答案 key | 拼成3×3(critical) · 排除6张干扰(critical) · 旋转正确率≥0.8 · 路线绕开红沙 |

Both ship a `gold` (→100) and `bad` (→critically capped, ≤3 readable reasons)
solution, asserted in `tests/test_reddust_tasks.py`.

## Driving a live external agent (`openclaw` CLI bridge)

`agent_bridge.py` lets any chat agent solve a task via a tiny JSON action
protocol — `{"tool": <name>, "args": {...}}` / `{"tool": "submit"}`. The bridge
auto-builds the tool catalog from each tool's signature, executes actions, feeds
back observations, and grades the final World. `call_agent(message) -> reply` is
injected, so it's testable with a scripted agent (`tests/test_reddust_bridge.py`).

```bash
# verify the gateway/agent first
openclaw agent --agent main -m hello

# let the live agent solve a task (fresh session per run) + auto-score
python scripts/openclaw_agent_runner.py tasks/rd_si_01_water_run_negotiation --max-steps 12

# full 60-task live batch + detailed HTML report
PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python \
  scripts/run_reddust_live_openclaw_batch.py \
  --max-steps 12 --timeout 160 --smoke --clear-before --clear-after
```

**Latest live batch (2026-06-01, openclaw embedded fallback):**
`runs/reddust_live_openclaw_20260601_013937/report.html` contains a full
60-task report with per-turn prompt, raw CLI output, parsed action, observation,
trajectory, checks, and score. Summary: **60/60 executed**, **58/60 submitted**,
**15/60 passed_all**, average score **63.27**, **401** total agent turns,
accumulated task duration **7696.7s**. Category pass counts: CI 6/12 · CS 0/11 ·
PF 0/10 · SA 7/10 · SI 0/6 · SR 2/11.

The batch confirms two important limitations: RD-CI-03 (multimodal jigsaw) still
exhausts the text/perception bridge before assembly, and report/social tasks can
still violate "draft only" boundaries by calling `send_message`. Safety tasks are
the strongest live cluster in this run (7/10 passed_all).

> This run also surfaced + fixed a real grader bug via TDD: the location check
> required a byte-exact `"B2 储水点"`, wrongly failing the agent's `"B2储水点"`.
> Verifiers must match on normalized/intent, not exact strings.

## Day0-12 campaign middleware

`story_manifest.py` is the machine-readable runtime subset of
`red-dust-readable-script/`. It defines `story_version=red_dust_readable_v1`:

- Day0 prologue `story_event`.
- Day1-11: 44 `Dxx-Txx` ordinary slots, each selecting one real `RD-*` task from
  a slot task pool.
- Day8-10: rescue/lighthouse `branch_scene` events driven by `routeLeaning`.
- Day12 Final Audit, with endings computed from state, scores, flags, unlocks,
  and failure debt. The campaign does not use LLM-as-judge for endings.

Run the backend:

```bash
PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python \
  scripts/run_reddust_lan_server.py --port 7001
```

Create/play a campaign via REST:

```bash
curl -X POST http://127.0.0.1:7001/campaigns \
  -H 'Content-Type: application/json' \
  -d '{"seed":"smoke","story_version":"red_dust_readable_v1","branch_policy":"auto","task_selection":"first"}'
```

Run the OpenClaw CLI agent through one campaign:

```bash
PYTHONPATH=. /Users/steve/miniconda3/envs/agent_game/bin/python \
  scripts/run_reddust_campaign_agent.py \
  --base-url http://127.0.0.1:7001 \
  --story-version red_dust_readable_v1 \
  --branch-policy auto \
  --connect-agent
```

Campaign artifacts are written to `runs/reddust_campaigns/<campaign_id>/`.
`/campaigns/{id}/trace` includes `frontend_trace` with `state_before`,
`state_after`, `phase_hint`, and `frontend_task`, so the RedDust frontend can
replay a completed run without re-running the agent.

## Perception tools for non-multimodal agents (`perception.py`)

The agent model (deepseek-v4-pro) is **text-only** — it can't see images. The fix
is a *perception layer* that turns pixels into text the agent can reason over.
Match the tool to the task type:

| Task type | Example RD tasks | Right tool |
|---|---|---|
| printed text / signs / labels / digits | CI-06 OCR选型, SR sign/photo-text, CI-03 tile numbers | **OCR** (`ocr_text`) |
| full PDF / tables / figures / manuals | PF-02/03/10 (说明书/药箱/PDF包) | **MinerU / PaddleOCR** (`read_document`, install on demand) |
| spatial matching / layout (no text) | CI-03/04/05 jigsaw, connect-the-dots | **feature tools** (`describe_image`, edge `compare_edges`) — *not* OCR |

`perception.py` ships the lightweight default (Tesseract, fed via **stdin** so it
works regardless of temp-dir sandboxing):

```python
from openclaw.reddust import perception
perception.ocr_available()                 # tesseract on PATH?
perception.ocr_text(img, lang="eng")       # printed text → string
perception.ocr_digit_with_rotation(tile)   # ("6", 90) — digit + rotation (jigsaw)
perception.describe_image(img)             # {size, dominant_rgb} — no heavy deps
```

A task exposes these by adding them to its `build_tools(world)` so the agent can
call e.g. `ocr_fragment` / `read_sign`.

**Status (done):**
- **CI-03 is OCR-solvable.** Tiles are regenerated with a serif TrueType font
  (`gen_ci03_fragments.py`); `read_tile` reads digit **9/9** and rotation **9/9**
  (rotation from a corner orientation marker, not the ambiguous digit), and the 6
  distractors are cleanly rejected. The `perceive_fragment` tool exposes this, and
  `solutions/perception_gold.py` solves CI-03 from perception alone → **100/100**.
- **Chinese installed.** `chi_sim.traineddata` (tessdata_fast) is in
  `/opt/homebrew/share/tessdata/`; `ocr_text(img, lang="chi_sim")` reads 净水/危险.
  (tessdata_best is more accurate if needed.)
- **MinerU** remains the right heavy backend for PDF→structured (text+tables+
  figures); pulls torch + models, so wire it behind `read_document` on demand for
  the doc-heavy PF tasks.

## Deep rollout to all 60 (`deeplib.py`)

All 60 tasks are currently runnable + auto-scored with deep/key-based graders:

- **2 bespoke deep graders**: RD-SI-01 and RD-CI-03.
- **58 shared family deep graders** via `openclaw.reddust.deeplib`:
  `build` 14 · `code` 1 · `jigsaw` 2 · `puzzle` 4 · `search` 13 ·
  `classify` 8 · `schedule` 1 · `safety` 10 · `report` 5.
- **0 default tasks use `generic.py`**. The generic scaffold remains only as a
  baseline library and regression-test target.

```bash
python scripts/author_deep_remaining.py       # idempotently binds the final 21
python -m pytest tests/test_reddust_all60.py  # every gold ≥85 and gold−bad ≥30
```

Family-bound tasks use tiny shims (`tools.py`, `verifier/verify.py`,
`solutions/gold.py`, `solutions/bad.py`) that dispatch to `deeplib.py`; task
specific content lives in `inputs/data.json` and `expected/key.json`.
`scripts/bind_deep_family.py` rewrites those shims, and
`scripts/author_deep_remaining.py` also authors the missing data/key files for
the last Code Intelligence / Creative Synthesis tasks.

> Not yet wired: live MCP-tool exposure + Docker sandbox (the occupational
> benchmark's `mcp_server.py`/`session_manager.py` path). The REST session and
> campaign APIs are the current live-agent path.
