# s01: The Agent Loop: "One loop & Bash is all you need"

## Concept
The model can't act on its own. Each response is a list of content blocks, either `text` or `tool_use` (a request such as "run `ls` for me"), plus a `stop_reason`:
- `"tool_use"`: the model is waiting for tool results.
- `"end_turn"`: the model is finished.

The harness runs what the model asks for and reports back:

```
messages ──> model ──> response
   ▲                     │ append as {"role":"assistant"}
   │          stop_reason == "tool_use"? ── no ──> return
   │                     │ yes
   └── append {"role":"user", content:[tool_result...]} <── run each tool_use
```

**The model decides when to stop. Your code never decides that.** There's no planner or router. The `while` loop is the agent, and every later chapter adds things around this loop without changing it.

Protocol rules:
1. Tool results go back as a **user** message. Each `tool_result` carries the `tool_use_id` of the request it answers.
2. N `tool_use` blocks in one reply → all N results go back together in **one** user message.

## Check-in
1. What would the API do if you sent the next request without a `tool_result` for a `tool_use` it made, and why?
2. The model has no memory between calls. So where does its "memory" of the last 5 tool runs actually live?
3. `run_bash` returns `stdout + stderr`. Why give the model stderr instead of hiding errors from it?

_Answers:_ (pending)

## Spec
File: `my_harness/agent.py`. Tests: `my_harness/tests/test_s01_agent_loop.py` (9 tests).
- `TOOLS`: a list with one tool, `bash`. Its `input_schema` is an object with a required string `command`.
- `run_bash(command: str) -> str`: runs in a shell and returns stdout + stderr, stripped.
  - No output → `"(no output)"`.
  - Timeout → a string starting with `"Error"`.
- `agent_loop(messages, client, model, system="")`: changes `messages` in place and returns `None`.
  - Calls `client.messages.create(model=, system=, messages=, tools=TOOLS, max_tokens=)`.
  - The client is passed in, so the tests can inject the fake.
- REPL under `if __name__ == "__main__":`: `load_dotenv()`, a real `Anthropic()` client (created only here), one `history` across turns, prints the final text.

Docs: https://docs.claude.com/en/docs/agents-and-tools/tool-use/overview

Live task: `python -m my_harness.agent`, then ask: "how many .py files are in s01_agent_loop, and what's the biggest?"

## Hints given
- (none)

## Review
- (pending)

## Compare
- (pending)
