from fake_client import FakeClient, response, text, tool_use

from my_harness.agent import TOOLS, agent_loop, run_command


# --- the tool ---------------------------------------------------------------

def test_tools_declares_a_single_bash_tool():
    assert [t["name"] for t in TOOLS] == ["bash"]
    schema = TOOLS[0]["input_schema"]
    assert schema["type"] == "object"
    assert "command" in schema["properties"]
    assert schema["required"] == ["command"]


def test_run_command_returns_stdout():
    assert run_command("echo hello") == "hello"


def test_run_command_includes_stderr():
    assert "oops" in run_command("echo oops 1>&2")


def test_run_command_reports_empty_output():
    assert run_command("true") == "(no output)"


# --- the loop ---------------------------------------------------------------

def test_plain_answer_makes_one_call_and_stops():
    client = FakeClient([response(text("hi there"))])
    messages = [{"role": "user", "content": "hello"}]

    agent_loop(messages, client, model="m")

    assert len(client.calls) == 1
    assert len(messages) == 2
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"][0].text == "hi there"


def test_model_receives_model_tools_and_history():
    client = FakeClient([response(text("ok"))])
    agent_loop([{"role": "user", "content": "x"}], client, model="my-model")

    call = client.calls[0]
    assert call["model"] == "my-model"
    assert call["tools"] == TOOLS
    assert call["messages"] == [{"role": "user", "content": "x"}]
    assert "max_tokens" in call


def test_tool_call_is_executed_and_result_fed_back():
    call = tool_use("bash", command="echo 42")
    client = FakeClient([response(call), response(text("the answer is 42"))])
    messages = [{"role": "user", "content": "what is echo 42?"}]

    agent_loop(messages, client, model="m")

    # user, assistant(tool_use), user(tool_result), assistant(text)
    assert [m["role"] for m in messages] == ["user", "assistant", "user", "assistant"]
    results = messages[2]["content"]
    assert results == [{"type": "tool_result", "tool_use_id": call.id, "content": "42"}]
    # the second model call must already see the tool result
    assert client.calls[1]["messages"][-1] is messages[2]


def test_parallel_tool_calls_all_get_results_in_one_message():
    a = tool_use("bash", command="echo a")
    b = tool_use("bash", command="echo b")
    client = FakeClient([response(text("running two"), a, b), response(text("done"))])
    messages = [{"role": "user", "content": "go"}]

    agent_loop(messages, client, model="m")

    results = messages[2]["content"]
    assert [r["tool_use_id"] for r in results] == [a.id, b.id]
    assert [r["content"] for r in results] == ["a", "b"]


def test_loop_keeps_going_until_model_stops_calling_tools():
    client = FakeClient([
        response(tool_use("bash", command="echo 1")),
        response(tool_use("bash", command="echo 2")),
        response(tool_use("bash", command="echo 3")),
        response(text("finished")),
    ])
    messages = [{"role": "user", "content": "count"}]

    agent_loop(messages, client, model="m")

    assert len(client.calls) == 4
    assert len(messages) == 8


# --- the REPL ---------------------------------------------------------------

def test_repl_keeps_one_history_across_turns(monkeypatch, capsys):
    """The REPL under __main__ must send earlier turns back with each new question."""
    import builtins, runpy, warnings
    import anthropic, dotenv

    fake = FakeClient([response(text("first answer")), response(text("second answer"))])
    monkeypatch.setattr(anthropic, "Anthropic", lambda *a, **k: fake)
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *a, **k: None)

    queries = iter(["what's the current directory?", "what files are in it?", "q"])

    def fake_input(prompt=""):
        try:
            return next(queries)
        except StopIteration:
            raise EOFError

    monkeypatch.setattr(builtins, "input", fake_input)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)  # runpy: module already imported
        try:
            runpy.run_module("my_harness.agent", run_name="__main__")
        except (SystemExit, EOFError):
            pass

    assert len(fake.calls) == 2, "expected one model call per question"
    second = fake.calls[1]["messages"]
    # the second question must arrive with the first turn still in the history
    assert [m["role"] for m in second] == ["user", "assistant", "user"]
    assert second[0]["content"] == "what's the current directory?"
    assert second[-1]["content"] == "what files are in it?"
    # and the final answers are printed
    out = capsys.readouterr().out
    assert "first answer" in out and "second answer" in out
