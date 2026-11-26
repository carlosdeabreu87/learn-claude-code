"""Offline stand-in for anthropic.Anthropic: replays scripted responses and records every call."""
from types import SimpleNamespace
import itertools

_ids = itertools.count(1)


def text(t):
    return SimpleNamespace(type="text", text=t)


def tool_use(name, **input):
    return SimpleNamespace(type="tool_use", id=f"toolu_{next(_ids):03d}", name=name, input=input)


def response(*blocks, stop_reason=None):
    if stop_reason is None:
        stop_reason = "tool_use" if any(b.type == "tool_use" for b in blocks) else "end_turn"
    return SimpleNamespace(content=list(blocks), stop_reason=stop_reason)


class FakeClient:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []  # kwargs of each messages.create call, messages snapshotted
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        snap = dict(kwargs)
        snap["messages"] = list(kwargs.get("messages", []))
        self.calls.append(snap)
        if not self._responses:
            raise AssertionError("agent called the model more times than the script allows")
        return self._responses.pop(0)
