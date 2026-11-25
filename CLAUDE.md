# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A teaching repository on **harness engineering**: how to build the code that gives an LLM (Claude) tools, knowledge, context management, and permissions so it can act as an agent. It is not a product or a library — it is 20 progressive lessons, each adding exactly one mechanism on top of a single unchanging agent loop (`while stop_reason == "tool_use": call LLM -> execute tools -> append results`).

Two tracks coexist:
- **Current track (canonical):** root-level `s01_agent_loop/` ... `s20_comprehensive/`. Each folder is one chapter.
- **Legacy track (kept for old links / the web app):** `agents/s01_agent_loop.py` ... `agents/s12_worktree_task_isolation.py` plus `agents/s_full.py`, and `docs/{en,ja,zh}/`. Legacy and current chapter numbers do **not** map 1:1 (see the mapping table in `README.md`) — never mix them up.

## Commands

```sh
pip install -r requirements.txt
cp .env.example .env            # set ANTHROPIC_API_KEY and MODEL_ID

# Run any chapter (current track) — each is standalone and runnable on its own
python s01_agent_loop/code.py
python s08_context_compact/code.py
python s20_comprehensive/code.py

# Run legacy chapter scripts
python agents/s01_agent_loop.py
python agents/s_full.py

# Tests (pytest, from repo root)
python -m pytest tests -q
python -m pytest tests/test_todo_write_string_input.py -q     # single file
python -m pytest tests/test_agents_smoke.py::test_agent_scripts_exist -q   # single test

# Web app (renders the LEGACY docs/ track only, not the current s01-s20 track)
cd web && npm install
npm run dev      # http://localhost:3000 — runs `extract` (scripts/extract-content.ts) first via predev
npm run build    # static export (next.config.ts: output: "export")
npx tsc --noEmit # type check (what CI runs)
```

CI (`.github/workflows/test.yml`, `ci.yml`) runs `pytest tests -q` against `requirements.txt`, and `npm ci && npx tsc --noEmit && npm run build` inside `web/`.

Tests have no live API dependency: course modules that import `anthropic`/`dotenv`/`yaml` get those modules faked via `sys.modules` injection (see `tests/test_todo_write_string_input.py`) so chapter code can be imported and exercised without network calls or a real key. Other tests (`test_agents_smoke.py`) just `py_compile` every legacy script to catch syntax errors.

## Architecture: the thing that never changes

Every chapter's code is built around this loop, verbatim in spirit:

```python
def agent_loop(messages):
    while True:
        response = client.messages.create(model=MODEL, system=SYSTEM, messages=messages, tools=TOOLS)
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            return
        results = [...]  # execute each tool_use block, collect tool_result
        messages.append({"role": "user", "content": results})
```

Reading any chapter's `code.py`, look for exactly what it adds relative to the previous chapter — nothing else should have changed. The one-mechanism-per-chapter discipline is the point of the repo; a diff that touches the loop itself, or bundles two mechanisms, breaks the pedagogy.

Per-chapter mechanism map (current track), each the subject of one `sNN_*/code.py`:

| # | Mechanism | What it bolts onto the loop |
|---|---|---|
| s01 | Agent Loop | one tool (bash) + the loop itself |
| s02 | Tool Use | `TOOL_HANDLERS` dispatch map, multiple tools |
| s03 | Permission | `PermissionRule` / approval gate before tool execution |
| s04 | Hooks | `PreToolUse`/`PostToolUse` extension points around tool calls |
| s05 | TodoWrite | plan-then-execute via a todo list tool |
| s06 | Subagent | spawns a fresh `messages[]` for side work, returns only the result |
| s07 | Skill Loading | on-demand injection of skill files (see `skills/`) instead of upfront context |
| s08 | Context Compact | snipCompact / microCompact / toolResultBudget / autoCompact strategies |
| s09 | Memory | selection / extraction / consolidation subsystems |
| s10 | System Prompt | runtime, section-based prompt assembly instead of a hardcoded string |
| s11 | Error Recovery | retry, token escalation, fallback model, alternate path on failure |
| s12 | Task System | `TaskRecord` + `blockedBy` graph, persisted to disk |
| s13 | Background Tasks | threaded execution + notification queue so the agent keeps thinking |
| s14 | Cron Scheduler | durable, time-triggered tasks |
| s15 | Agent Teams | `MessageBus`, per-agent inbox, permission bubbling across teammates |
| s16 | Team Protocols | fixed request/reply format, shutdown handshake, plan approval |
| s17 | Autonomous Agents | idle-cycle self-organization, agents claim work from a board |
| s18 | Worktree Isolation | `WorktreeRecord` binds each task to its own directory |
| s19 | MCP Plugin | multi-transport external tools merged into the same tool pool |
| s20 | Comprehensive Agent | all of the above combined around the one loop |

The JSONL mailbox protocol (s15-s18) is a teaching implementation, not a claim about any production system's internals.

## Chapter folder shape

```
sNN_topic/
  README.md       # Chinese source of truth (complete narrative, written first)
  README.en.md    # English translation
  README.ja.md    # Japanese translation
  code.py         # standalone, runnable implementation — no cross-chapter imports
  images/          # SVG diagrams, only where a diagram earns its place
```

`code.py` in each chapter is self-contained by design (copy-paste runnable) rather than importing shared helpers from other chapters — that duplication is intentional, not an oversight to refactor away.

## Working in this repo

- **Keep teaching code minimal.** Do not add production hardening, defensive parsing, extra abstraction, or error-handling layers to a chapter's `code.py` unless that chapter's entire subject is that mechanism. A simplification that looks like a bug (e.g. a narrow dangerous-command blocklist in s01's `run_bash`) is usually deliberate — check the README's narrative or ask before "fixing" it.
- **Three-language sync is mandatory.** Any change to a chapter's `code.py` or README must be mirrored across `README.md` (Chinese source), `README.en.md`, and `README.ja.md` in that same chapter folder, with identical code blocks in all three.
- **Don't cross tracks.** Changes to the current `sNN_topic/` chapters are not expected to be back-ported to `agents/` or `docs/` (legacy), and vice versa — they are intentionally allowed to drift during the transition.
- **One PR, one issue.** Per `CONTRIBUTING.md`, PRs should be tied to a specific issue and scoped to one problem; PRs that expand a chapter's scope/structure, or that "fix" a deliberate simplification, get closed without detailed review.
- **`MODEL_ID` and `ANTHROPIC_BASE_URL`** make every chapter work against Anthropic-compatible third-party providers (MiniMax, GLM, Kimi, DeepSeek) in addition to Anthropic directly — see `.env.example` for the current model IDs and endpoints per provider/region.
- **The `web/` app** is a Next.js static-export site that renders the *legacy* 12-lesson `docs/` track (via `scripts/extract-content.ts`, run automatically by `predev`/`prebuild`), not the current 20-lesson root track. Don't expect it to reflect edits made to `sNN_topic/`.
