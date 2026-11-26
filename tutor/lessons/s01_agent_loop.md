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

_Restarted on learner's request (2026-11-25), with the problem framing, a worked message timeline, and the production note added._

**Problem:** without a loop, *you* are the middle layer: the model prints a command, you run it, paste the output back, repeat. The loop automates the human in the middle.

Worked timeline for "how many .py files are here?":
```
[0] user       "how many .py files are here?"
[1] assistant  [text "Let me check", tool_use id=A bash{"command":"ls *.py | wc -l"}]   stop_reason=tool_use
[2] user       [tool_result tool_use_id=A content="3"]
[3] assistant  [text "There are 3 .py files."]                                          stop_reason=end_turn
```

Production note: Claude Code checks for `tool_use` *blocks* rather than trusting `stop_reason`, because with streaming the stop reason can arrive after the blocks. Same idea, sturdier signal.

**The model decides when to stop. Your code never decides that.** There's no planner or router. The `while` loop is the agent, and every later chapter adds things around this loop without changing it.

Protocol rules:
1. Tool results go back as a **user** message. Each `tool_result` carries the `tool_use_id` of the request it answers.
2. N `tool_use` blocks in one reply → all N results go back together in **one** user message.

### Warm-up (added on the second restart)
In a Python REPL, the learner is the loop: make one `messages.create` call with the bash tool, inspect `content` and `stop_reason`, run the command by hand, and send back a `tool_result`. Observe the second response.

Warm-up log (2026-11-25, learner's notebook `tutor/lessons/s01_python_REPL.ipynb`; asked to move it to `my_harness/scratch/`):
- They rebuilt the assistant turn by hand without `name` and with `input` as the command string, not the dict, so the API returned a 400: `messages.1.content.0.tool_use.name: Field required`. Explained that the assistant turn must be echoed back exactly, and the easiest way is `"content": response.content`.
- The second call passes `tools=tools`, but they defined `TOOLS`.
- They hadn't yet appended the `tool_result` user message. Told them they would hit that error next, and that it answers check-in Q1.
- **Warm-up completed** (20:45). They echoed `response.content` back as the assistant turn, ran the command with `subprocess.run`, sent the `tool_result`, and got `end_turn` with the answer. They also tried "capital of France?", got `end_turn` with no tool call, and saw that the model decides whether to use a tool at all.
- Feedback given:
  - The second response began with a `ThinkingBlock` before the `TextBlock`, so indexing `content[0]` or `content[1]` breaks. Loop over the blocks and filter by `type`.
  - They captured only `.stdout`, so stderr is lost. That's Q3.
  - They skipped the experiment of calling again without the `tool_result` (Q1).

## Check-in
1. What would the API do if you sent the next request without a `tool_result` for a `tool_use` it made, and why?
2. The model has no memory between calls. So where does its "memory" of the last 5 tool runs actually live?
3. `run_bash` returns `stdout + stderr`. Why give the model stderr instead of hiding errors from it?

_Answers:_
- Q1, learner: "it returns an error saying that there is a tool_use request without a corresponding tool_result." That's correct for the *what*. Added the *why*: the API requires every `tool_use` to be answered by a `tool_result` in the very next user message, so the history stays consistent. Without the result, the model would be continuing from an action whose outcome it never saw. Flagged that this pairing rule comes back in s08 (compaction must not split a pair) and in s11 (recovering from errors).
- Q2, learner: the harness appends the model's full `response.content` and the tool results to `messages`, and the model rereads that list on each call. Correct. Added: the list lives in the harness's process, not on the server. It's resent in full every call, so cost and length grow each turn (which motivates s08 compaction). The harness fully controls what the model "remembers" (s09 memory, s10 prompt assembly).
- Q3, learner: stderr carries the error message, so the model can see what failed and ask for actions to fix it. Correct. Added: without stderr, a failed command often looks like empty output, so the model may assume it succeeded or retry blindly. Errors are information, and self-correction depends on seeing them (comes back in s11).
- Check-in complete. Moved to step 4 (Build).

## Spec
File: `my_harness/agent.py`. Tests: `tutor/tests/test_s01_agent_loop.py` (9 tests).
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
