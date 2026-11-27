# Progress

**Current:** s01 Agent Loop, **step 4 (Build)**: 10/10 tests pass as of 2026-11-27. All spec items done and the live task works (2026-11-27). Next: step 5 (Review) when the learner says done.

**Resume here:** greet the learner, restate the step 4 task in short form (the spec is in `lessons/s01_agent_loop.md` under "Spec"), and remind them of the two warm-up lessons:
1. Iterate over `response.content` by `.type`, never index it. A `ThinkingBlock` can come first.
2. `run_command` (learner's name for `run_bash`) must return stdout **+ stderr**.

The learner writes `my_harness/agent.py` (it doesn't exist yet) until `.venv/bin/python -m pytest tutor/tests -q` shows 10 passed, then runs it live with `python -m my_harness.agent`. When they say it's done, go to step 5 (Review).

Done so far in s01: concept taught (restarted twice at the learner's request), hands-on warm-up in a notebook (completed), and the check-in (Q1–Q3 all answered correctly; answers and corrections are recorded in the lesson file).

## Setup
- [x] Branch `learn/carlos`, `.venv` (Python 3.11) with requirements + pytest + ipykernel
- [x] `tutor/tests/fake_client.py`, `tutor/tests/conftest.py`
- [x] `.env` with `ANTHROPIC_API_KEY` and `MODEL_ID` (learner)
- [x] Folder split: `my_harness/` belongs only to the learner; `tutor/` holds the tutor's files

## Chapters
| Ch | Topic | Status |
|---|---|---|
| s01 | Agent Loop | in progress |
| s02 | Tool Use | |
| s03 | Permission | |
| s04 | Hooks | |
| s05 | TodoWrite | |
| s06 | Subagent | |
| s08 | Context Compact | |
| s09 | Memory | |
| s10 | System Prompt | |
| s11 | Error Recovery | |
| s12 | Task System | |
| s13 | Background Tasks | |
| s14 | Cron Scheduler | |
| s15 | Agent Teams | |
| s16 | Team Protocols | |
| s17 | Autonomous Agents | |
| s18 | Worktree Isolation | |
| s07 | Skill Loading | |
| s19 | MCP Plugin | |
| s20 | Comprehensive | |

## Open items
- **Learner's pending task (2026-11-27):** add comments to `my_harness/agent.py`. Ask about it before the s01 Review starts.
- The learner's warm-up notebook is at `tutor/lessons/s01_python_REPL.ipynb`. They should move it to `my_harness/scratch/`.
- `git push` to origin (`carlosdeabreu87/learn-claude-code`) failed with `Permission denied (publickey)`. The learner needs to set up an SSH key or switch to HTTPS. Commit `011f06c` is local only.
- ~~Uncommitted work~~: resolved, committed by 2026-11-26 (`e6d2517` onward).
