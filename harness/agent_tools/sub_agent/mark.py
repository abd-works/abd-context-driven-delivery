"""@subAgent mark — prepend non-blocking delegation instructions to agent ops."""
from __future__ import annotations

from typing import Any, Callable

SUB_AGENT_CALLER_PREAMBLE = """Hand work to a background sub-agent and continue without waiting.

Do not perform the delegated work in this conversation. Do not wait for the
sub-agent to finish.

Launch the Task tool with run_in_background true and subagent_type
generalPurpose. Pass the instructions below as the task prompt.

Tell the user you launched a non-blocking sub-agent and summarize what you delegated."""


def marked_as_sub_agent(callable: Any) -> bool:
    return bool(getattr(callable, "_sub_agent", False))


def prepend_sub_agent_instructions(text: str) -> str:
    preamble = SUB_AGENT_CALLER_PREAMBLE.strip()
    body = (text or "").strip()
    if not body:
        return preamble
    return f"{preamble}\n\n{body}"


class SubAgentMark:
    """Mark an @agent_tool or @agent_instructions member for non-blocking sub-agent launch."""

    flag = "_sub_agent"

    def __new__(cls, fn: Callable[..., Any] | None = None):
        mark = object.__new__(cls)
        if callable(fn):
            return mark.annotate(fn)
        return mark

    def annotate(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        setattr(fn, self.flag, True)
        return fn

    def __call__(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        return self.annotate(fn)


subAgent = SubAgentMark()
