# Glossary

Important terms, in alphabetical order, added as the lessons go. Each entry says which chapter it first came up in. Definitions are short and use this course's examples. Follow the links for depth.

---

**400 Bad Request** *(s01)*
The HTTP error the API returns when it rejects the request you sent. The message gives a path to the problem, e.g. `messages.1.content.0.tool_use.name: Field required` means `messages[1]` → `content[0]` → field `name` is missing.

**Agent** *(s01)*
A model that acts in an environment by deciding which tools to call and when to stop, in a loop. In this course: **agent = model + harness**. The intelligence comes from the model; the harness provides the hands.

**Agent loop** *(s01)*
The `while` loop at the core of every agent. Call the model → if `stop_reason == "tool_use"`, run the tools, append the results, and repeat; otherwise stop. Every later chapter adds code around it without changing it.

**Anthropic client** *(s01)*
The object from the `anthropic` Python SDK (`Anthropic()`) that sends requests to the API. It reads `ANTHROPIC_API_KEY` from the environment. Call the model with `client.messages.create(...)`.

**Assistant message** *(s01)*
A message with `role: "assistant"`, i.e. what the model said. The harness appends `response.content` to `messages` unchanged, so the model sees its own past turns.

**Content block** *(s01)*
One item in a message's `content` list. Types you've seen: `text`, `tool_use`, `tool_result` and `thinking`. A single response can mix several, in any order, so iterate over them and check `.type`, never index by position.

**Context window** *(s01)*
The maximum amount of text (measured in tokens) the model can read in one call: system prompt, tools and the whole `messages` list. Since `messages` grows each turn, you eventually hit it. See s08, compaction.

**.env / python-dotenv** *(s01)*
`.env` is a file of `KEY=value` lines (API key, `MODEL_ID`) kept out of git. `load_dotenv()` copies those lines into environment variables so `os.environ["MODEL_ID"]` works.

**end_turn** *(s01)*
The `stop_reason` value meaning "I'm finished, no tool needed". It tells the loop to exit.

**Fake client (test double)** *(s01)*
A stand-in for the real `Anthropic` client that plays back scripted responses (`tutor/tests/fake_client.py`). Tests run offline, free and repeatably. This works because `agent_loop` receives the client as an argument (dependency injection).

**Harness** *(s01)*
All the code around the model that lets it work in a domain: **tools + knowledge + observation + actions + permissions**. "The model is the driver; the harness is the vehicle." That's what you're building.

**input_schema** *(s01)*
Part of a tool definition: a JSON Schema describing the tool's arguments (`{"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}`). The model uses it to produce a valid `input`.

**Jupyter notebook / kernel** *(s01)*
A `.ipynb` file of code cells whose output stays under each cell. It's JSON underneath, so an empty file is invalid. The *kernel* is the Python process that runs the cells. Pick the `.venv` one. Variables stay alive between cells, as in a REPL.

**LLM (Large Language Model)** *(s01)*
A neural network trained on huge amounts of text that predicts what comes next. Claude is one. It has no memory between calls and can't run anything itself: it only produces content blocks.

**max_tokens** *(s01)*
A required argument to `messages.create`: the maximum length of the model's reply, in tokens. If the model reaches it mid-answer, `stop_reason` becomes `"max_tokens"`. See s11.

**Messages API** *(s01)*
Anthropic's endpoint for talking to Claude: send `model`, `system`, `messages`, `tools` and `max_tokens`, and get back `content` blocks plus a `stop_reason`. [Docs](https://docs.claude.com/en/api/messages)

**`messages` (conversation history)** *(s01)*
The list of `{"role": ..., "content": ...}` dicts the harness keeps and resends **in full** on every call. It's the model's only "memory", and it lives in your process, not on the server.

**REPL (Read–Eval–Print Loop)** *(s01)*
An interactive prompt (`python` with no file) that reads a line, runs it, prints the result and waits for the next line. Your `agent.py` main block is also a REPL: read a question → run the agent loop → print the answer.

**Role** *(s01)*
Who a message is from: `"user"` (you, **or the harness sending tool results**) or `"assistant"` (the model). Messages alternate between user and assistant.

**SDK (Software Development Kit)** *(s01)*
A library that wraps an API in friendly code. Here it's the `anthropic` Python package: `Anthropic()`, `messages.create`, and block objects like `ToolUseBlock`.

**stdout / stderr** *(s01)*
A process's two output streams: normal output and error messages. `run_bash` returns **both**, so when a command fails the model sees why and can fix it.

**stop_reason** *(s01)*
Why the model stopped generating: `"tool_use"` (waiting for tool results), `"end_turn"` (done) or `"max_tokens"` (cut off). It's the signal the agent loop branches on.

**subprocess** *(s01)*
The Python module for running external commands. `subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=...)` runs a shell command and captures its stdout and stderr.

**System prompt** *(s01)*
The `system` argument: standing instructions that frame every call ("You are a coding agent at /path..."). It's sent separately from `messages`. s10 builds it from parts at runtime.

**Thinking block** *(s01)*
A `type: "thinking"` content block holding the model's reasoning before it answers. It can come *before* the text block, which is why `content[0]` isn't always the answer. It's a block, not a message: it sits inside an assistant message's `content` list. In the SDK it's a `ThinkingBlock` with fields `type` (`"thinking"`), `thinking` (the reasoning text) and `signature` (a check value the API uses to verify it when you send the block back). It has no `.text`. A related block type, `redacted_thinking`, holds encrypted reasoning in `data`. Keep thinking blocks in the history unchanged. See https://docs.claude.com/en/docs/build-with-claude/extended-thinking

**Token** *(s01)*
The unit models read and write in, roughly ¾ of an English word. Context limits, `max_tokens` and pricing are all counted in tokens.

**Tool** *(s01)*
An action the harness offers the model, declared with `name`, `description` and `input_schema`, and implemented by a handler function (e.g. `bash` → `run_bash`). The model asks for it; the harness runs it.

**tool_result** *(s01)*
The block the harness sends back in a **user** message: `{"type": "tool_result", "tool_use_id": ..., "content": output}`. Every `tool_use` must get one in the very next message, or the API returns a 400.

**tool_use** *(s01)*
A content block in which the model asks for a tool to be run. It has `id`, `name` and `input`. When it's present, `stop_reason` is `"tool_use"`.

**tool_use_id** *(s01)*
The `id` of a `tool_use` block, repeated in its `tool_result` so the model knows which result answers which request. This matters when it calls several tools at once.

**Virtual environment (venv)** *(s01)*
An isolated Python installation for one project (`.venv/`), with its own packages and version (3.11 here). Activate it with `source .venv/bin/activate`.
